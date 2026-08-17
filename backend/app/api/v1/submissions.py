from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.v1.auth import get_current_user
from app.api.v1.users import is_valid_image_content
from app.db.session import get_db
from app.models.character import Character
from app.models.haki_record import HakiRecord
from app.models.meme import Meme
from app.models.music_track import MusicTrack
from app.models.submission import Submission
from app.models.user import User
from app.schemas.submission import SubmissionRead


router = APIRouter()


PROJECT_ROOT = Path(__file__).resolve().parents[4]
STORAGE_DIR = PROJECT_ROOT / "storage"
SUBMISSION_DIR = STORAGE_DIR / "uploads" / "submissions"

ALLOWED_MEME_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}

ALLOWED_MUSIC_TYPES = {
    "audio/mpeg": ".mp3",
    "audio/mp3": ".mp3",
}

ALLOWED_SUBMISSION_TYPES = {"meme", "music"}
ALLOWED_SUBMISSION_STATUSES = {"pending", "approved", "rejected"}

MAX_MEME_SIZE = 10 * 1024 * 1024
MAX_MUSIC_SIZE = 30 * 1024 * 1024
PUBLISH_HAKI_VALUE = 10


def is_valid_mp3_content(content: bytes) -> bool:
    if content.startswith(b"ID3"):
        return True

    return len(content) >= 2 and content[0] == 0xFF and content[1] & 0xE0 == 0xE0


def save_upload_file(content: bytes, folder: Path, suffix: str) -> str:
    folder.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid4().hex}{suffix}"
    file_path = folder / filename
    file_path.write_bytes(content)

    relative_path = file_path.relative_to(STORAGE_DIR)

    return f"/static/{relative_path.as_posix()}"


def clean_optional(value: str | None) -> str | None:
    if value is None:
        return None

    return value.strip() or None


@router.post("", response_model=SubmissionRead)
async def create_submission(
    submission_type: str = Form(...),
    title: str = Form(...),
    description: str | None = Form(default=None),
    character_id: int | None = Form(default=None),
    character_ids: list[int] = Form(default=[]),
    source_name: str | None = Form(default=None),
    source_url: str | None = Form(default=None),
    author_name: str | None = Form(default=None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if submission_type not in ALLOWED_SUBMISSION_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="投稿类型只支持 meme 或 music",
        )

    cleaned_title = title.strip()

    if not cleaned_title or len(cleaned_title) > 160:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="投稿标题长度应为 1 到 160 个字符",
        )

    if submission_type == "meme" and len(cleaned_title) > 120:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="表情包标题不能超过 120 个字符",
        )

    selected_character_ids = list(dict.fromkeys([
        *character_ids,
        *([character_id] if character_id is not None else []),
    ]))

    selected_characters: list[Character] = []

    if selected_character_ids:
        loaded_characters = db.scalars(
            select(Character).where(Character.id.in_(selected_character_ids))
        ).all()
        characters_by_id = {character.id: character for character in loaded_characters}

        if len(characters_by_id) != len(selected_character_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="关联角色不存在",
            )

        selected_characters = [characters_by_id[character_id] for character_id in selected_character_ids]

    primary_character_id = selected_character_ids[0] if selected_character_ids else None

    content_type = file.content_type

    if submission_type == "meme":
        allowed_types = ALLOWED_MEME_TYPES
        max_size = MAX_MEME_SIZE
        folder = SUBMISSION_DIR / "memes"
        type_error = "表情包只支持 jpg、png、webp、gif"
        size_error = "表情包文件不能超过 10MB"
    else:
        allowed_types = ALLOWED_MUSIC_TYPES
        max_size = MAX_MUSIC_SIZE
        folder = SUBMISSION_DIR / "music"
        type_error = "音乐投稿暂时只支持 mp3"
        size_error = "音乐文件不能超过 30MB"

    if content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=type_error,
        )

    content = await file.read(max_size + 1)

    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=size_error,
        )

    is_valid_content = (
        is_valid_image_content(content_type, content)
        if submission_type == "meme"
        else is_valid_mp3_content(content)
    )

    if not is_valid_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="投稿文件内容无效",
        )

    suffix = allowed_types[content_type]
    file_url = save_upload_file(
        content=content,
        folder=folder,
        suffix=suffix,
    )

    submission = Submission(
        user_id=current_user.id,
        submission_type=submission_type,
        status="approved",
        title=cleaned_title,
        description=clean_optional(description),
        file_url=file_url,
        character_id=primary_character_id,
        source_name=clean_optional(source_name),
        source_url=clean_optional(source_url),
        author_name=clean_optional(author_name) or current_user.username,
    )
    submission.characters = selected_characters

    db.add(submission)
    db.flush()

    if submission_type == "meme":
        published_content = Meme(
            slug=f"submission-meme-{submission.id}",
            title=cleaned_title,
            description=clean_optional(description),
            image_url=file_url,
            file_type="gif" if content_type == "image/gif" else "image",
            character_id=primary_character_id,
            source_name=clean_optional(source_name) or "用户投稿",
            source_url=clean_optional(source_url),
            author_name=clean_optional(author_name) or current_user.username,
            is_featured=False,
        )
    else:
        published_content = MusicTrack(
            slug=f"submission-music-{submission.id}",
            title=cleaned_title,
            description=clean_optional(description),
            audio_url=file_url,
            character_id=primary_character_id,
            source_name=clean_optional(source_name) or "用户投稿",
            source_url=clean_optional(source_url),
            author_name=clean_optional(author_name) or current_user.username,
            is_featured=False,
        )

    published_content.characters = selected_characters
    db.add(published_content)
    db.flush()

    submission.content_id = published_content.id
    current_user.haki_value += PUBLISH_HAKI_VALUE
    db.add(
        HakiRecord(
            user_id=current_user.id,
            change_value=PUBLISH_HAKI_VALUE,
            reason=f"作品发布：{cleaned_title}",
        )
    )

    db.commit()
    db.refresh(submission)

    return submission


@router.get("/me", response_model=list[SubmissionRead])
def list_my_submissions(
    status_filter: str | None = Query(default=None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if status_filter and status_filter not in ALLOWED_SUBMISSION_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="投稿状态无效",
        )

    statement = (
        select(Submission)
        .options(selectinload(Submission.characters))
        .where(Submission.user_id == current_user.id)
        .order_by(Submission.created_at.desc(), Submission.id.desc())
    )

    if status_filter:
        statement = statement.where(Submission.status == status_filter)

    return db.scalars(statement).all()
