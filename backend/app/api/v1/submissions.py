
from pathlib import Path
from hashlib import sha256
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload
from starlette.concurrency import run_in_threadpool

from app.api.v1.auth import get_current_user
from app.api.v1.users import is_valid_image_content
from app.db.session import get_db
from app.models.character import Character
from app.models.meme import Meme
from app.models.music_track import MusicTrack
from app.models.submission import Submission
from app.models.user import User
from app.schemas.submission import SubmissionRead, SubmissionUpdate
from app.services.content_status import populate_submission_content_statuses
from app.services.haki import add_haki
from app.services.video_audio import VideoAudioError, extract_music_from_video


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

ALLOWED_VIDEO_TYPES = {
    "video/mp4": ".mp4",
    "video/quicktime": ".mov",
    "video/webm": ".webm",
}

ALLOWED_SUBMISSION_TYPES = {"meme", "music"}
ALLOWED_MUSIC_SOURCE_TYPES = {"upload", "video_upload"}
ALLOWED_SUBMISSION_STATUSES = {"pending", "approved", "rejected", "deleted"}

MAX_MEME_SIZE = 10 * 1024 * 1024
MAX_MUSIC_SIZE = 30 * 1024 * 1024
MAX_VIDEO_SIZE = 200 * 1024 * 1024


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


async def save_video_upload(file: UploadFile, suffix: str) -> Path:
    temp_dir = STORAGE_DIR / "temp" / "video-imports"
    temp_dir.mkdir(parents=True, exist_ok=True)
    target_path = temp_dir / f"{uuid4().hex}{suffix}"
    total_size = 0

    try:
        with target_path.open("wb") as target_file:
            while chunk := await file.read(1024 * 1024):
                total_size += len(chunk)
                if total_size > MAX_VIDEO_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="视频文件不能超过 200MB",
                    )
                target_file.write(chunk)
    except Exception:
        target_path.unlink(missing_ok=True)
        raise

    if total_size == 0:
        target_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="视频文件为空",
        )

    return target_path


def clean_optional(value: str | None) -> str | None:
    if value is None:
        return None

    return value.strip() or None


def load_selected_characters(
    character_ids: list[int],
    db: Session,
) -> list[Character]:
    unique_character_ids = list(dict.fromkeys(character_ids))

    if not unique_character_ids:
        return []

    loaded_characters = db.scalars(
        select(Character).where(Character.id.in_(unique_character_ids))
    ).all()
    characters_by_id = {character.id: character for character in loaded_characters}

    if len(characters_by_id) != len(unique_character_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="关联角色不存在",
        )

    return [characters_by_id[character_id] for character_id in unique_character_ids]


@router.post("", response_model=SubmissionRead)
async def create_submission(
    submission_type: str = Form(...),
    title: str = Form(default=""),
    description: str | None = Form(default=None),
    character_id: int | None = Form(default=None),
    character_ids: list[int] = Form(default=[]),
    source_type: str = Form(default="upload"),
    source_name: str | None = Form(default=None),
    source_url: str | None = Form(default=None),
    author_name: str | None = Form(default=None),
    rights_confirmed: bool = Form(default=False),
    file: UploadFile | None = File(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if submission_type not in ALLOWED_SUBMISSION_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="投稿类型只支持 meme 或 music",
        )

    selected_character_ids: list[int] = []
    selected_characters: list[Character] = []

    if submission_type == "meme":
        selected_character_ids = list(dict.fromkeys([
            *character_ids,
            *([character_id] if character_id is not None else []),
        ]))
        selected_characters = load_selected_characters(selected_character_ids, db)

    primary_character_id = selected_character_ids[0] if selected_character_ids else None

    cleaned_source_type = source_type.strip().lower()
    cleaned_source_url = clean_optional(source_url)
    cleaned_title = title.strip()
    content_type = file.content_type if file is not None else None
    file_url = ""
    cover_url: str | None = None
    source_author: str | None = None
    duration_seconds: int | None = None
    image_hash: str | None = None

    if submission_type == "meme":
        if cleaned_source_type != "upload":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="表情包投稿只支持文件上传",
            )
        if not cleaned_title or len(cleaned_title) > 120:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="表情包标题长度应为 1 到 120 个字符",
            )
        if file is None or content_type not in ALLOWED_MEME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="表情包只支持 jpg、png、webp、gif",
            )

        content = await file.read(MAX_MEME_SIZE + 1)
        if len(content) > MAX_MEME_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="表情包文件不能超过 10MB",
            )
        if not is_valid_image_content(content_type, content):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="投稿文件内容无效",
            )

        image_hash = sha256(content).hexdigest()
        duplicate_meme_id = db.scalar(
            select(Meme.id).where(Meme.image_hash == image_hash)
        )
        if duplicate_meme_id is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="该图片已收录到表情包档案",
            )

        file_url = save_upload_file(
            content=content,
            folder=SUBMISSION_DIR / "memes",
            suffix=ALLOWED_MEME_TYPES[content_type],
        )

    else:
        if cleaned_source_type not in ALLOWED_MUSIC_SOURCE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="音乐来源只支持上传 MP3 或上传视频提取",
            )

        if cleaned_source_type == "upload":
            if not cleaned_title or len(cleaned_title) > 160:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="音乐标题长度应为 1 到 160 个字符",
                )
            if file is None or content_type not in ALLOWED_MUSIC_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="音乐投稿暂时只支持 MP3",
                )

            content = await file.read(MAX_MUSIC_SIZE + 1)
            if len(content) > MAX_MUSIC_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="音乐文件不能超过 30MB",
                )
            if not is_valid_mp3_content(content):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="投稿文件内容无效",
                )

            file_url = save_upload_file(
                content=content,
                folder=SUBMISSION_DIR / "music",
                suffix=ALLOWED_MUSIC_TYPES[content_type],
            )
        else:
            if file is None or content_type not in ALLOWED_VIDEO_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="视频提取支持 MP4、MOV、WebM 文件",
                )
            if not rights_confirmed:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="请确认你拥有该视频音频的收录与公开播放授权",
                )

            cleaned_title = cleaned_title or Path(file.filename or "视频提取音频").stem
            if not cleaned_title or len(cleaned_title) > 160:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="音乐标题长度应为 1 到 160 个字符",
                )

            temporary_video = await save_video_upload(
                file,
                ALLOWED_VIDEO_TYPES[content_type],
            )
            try:
                assets = await run_in_threadpool(
                    extract_music_from_video,
                    temporary_video,
                )
            except VideoAudioError as error:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(error),
                ) from error

            file_url = assets.audio_url
            cover_url = assets.cover_url
            duration_seconds = assets.duration_seconds
            source_author = clean_optional(author_name)

    submission = Submission(
        user_id=current_user.id,
        submission_type=submission_type,
        status="approved",
        title=cleaned_title,
        description=clean_optional(description),
        file_url=file_url,
        cover_url=cover_url,
        source_type=cleaned_source_type,
        character_id=primary_character_id,
        source_name=(
            "本地视频提取"
            if cleaned_source_type == "video_upload"
            else clean_optional(source_name)
        ),
        source_url=cleaned_source_url,
        source_author=source_author,
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
            image_hash=image_hash,
            file_type="gif" if content_type == "image/gif" else "image",
            character_id=primary_character_id,
            source_name=clean_optional(source_name) or "用户投稿",
            source_url=clean_optional(source_url),
            author_name=current_user.username,
            author_id=current_user.id,
            is_featured=False,
        )
    else:
        published_content = MusicTrack(
            slug=f"submission-music-{submission.id}",
            title=cleaned_title,
            description=clean_optional(description),
            audio_url=file_url,
            cover_url=cover_url,
            duration_seconds=duration_seconds,
            source_type=cleaned_source_type,
            character_id=primary_character_id,
            source_name=(
                "本地视频提取"
                if cleaned_source_type == "video_upload"
                else clean_optional(source_name) or "用户上传"
            ),
            source_url=cleaned_source_url,
            source_author=source_author,
            author_name=current_user.username,
            author_id=current_user.id,
            is_featured=False,
        )

    published_content.characters = selected_characters
    db.add(published_content)
    db.flush()

    submission.content_id = published_content.id
    add_haki(
        db,
        current_user,
        "upload_meme" if submission_type == "meme" else "upload_music",
        target_type=submission_type,
        target_id=published_content.id,
        reason=f"作品发布：{cleaned_title}",
    )

    db.commit()
    db.refresh(submission)

    return submission


@router.put("/{submission_id}", response_model=SubmissionRead)
def update_my_submission(
    submission_id: int,
    data: SubmissionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    submission = db.scalar(
        select(Submission)
        .options(selectinload(Submission.characters))
        .where(
            Submission.id == submission_id,
            Submission.user_id == current_user.id,
        )
    )

    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作品不存在，或你没有编辑权限",
        )

    if submission.content_deleted or submission.content_id is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该作品已下架，无法编辑",
        )

    title = data.title.strip()
    description = clean_optional(data.description)
    source_name = clean_optional(data.source_name)
    source_url = clean_optional(data.source_url)
    source_author = clean_optional(data.source_author)

    if submission.submission_type == "meme":
        if len(title) > 120:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="表情包标题不能超过 120 个字符",
            )

        if source_url and len(source_url) > 255:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="表情包来源链接不能超过 255 个字符",
            )

        content = db.get(Meme, submission.content_id)
        if content is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="正式表情包内容不存在，无法编辑",
            )
        if content.status != "active":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="该表情包已撤回或下架，无法编辑",
            )

        characters = load_selected_characters(data.character_ids, db)
        primary_character_id = characters[0].id if characters else None

        submission.character_id = primary_character_id
        submission.characters = characters
        content.character_id = primary_character_id
        content.characters = characters
        content.source_name = source_name or "用户投稿"
        content.source_url = source_url
    elif submission.submission_type == "music":
        content = db.get(MusicTrack, submission.content_id)
        if content is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="正式音乐内容不存在，无法编辑",
            )
        if content.status != "active":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="该音乐已撤回或下架，无法编辑",
            )

        content.source_name = source_name or "用户上传"
        content.source_url = source_url
        content.source_author = source_author
    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="作品类型无效，无法编辑",
        )

    submission.title = title
    submission.description = description
    submission.source_name = source_name
    submission.source_url = source_url
    submission.source_author = source_author
    content.title = title
    content.description = description

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
        .options(
            joinedload(Submission.user),
            selectinload(Submission.characters),
        )
        .where(
            Submission.user_id == current_user.id,
        )
        .order_by(
            Submission.created_at.desc(),
            Submission.id.desc()
        )
    )


    if status_filter:

        statement = statement.where(
            Submission.status == status_filter
        )


    submissions = db.scalars(statement).all()
    populate_submission_content_statuses(db, submissions)
    return submissions
