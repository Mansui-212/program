from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.submission import Submission
from app.models.user import User
from app.schemas.user import UserPublicRead, UserPublicSubmissionRead, UserRead


router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parents[4]
STORAGE_DIR = PROJECT_ROOT / "storage"
AVATAR_DIR = STORAGE_DIR / "images" / "avatars"

ALLOWED_AVATAR_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}

MAX_AVATAR_SIZE = 2 * 1024 * 1024


def is_valid_image_content(content_type: str, content: bytes) -> bool:
    signatures = {
        "image/jpeg": (b"\xff\xd8\xff",),
        "image/png": (b"\x89PNG\r\n\x1a\n",),
        "image/gif": (b"GIF87a", b"GIF89a"),
    }

    if content_type == "image/webp":
        return content.startswith(b"RIFF") and content[8:12] == b"WEBP"

    return content.startswith(signatures.get(content_type, ()))


@router.post("/me/avatar", response_model=UserRead)
async def upload_my_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    content_type = file.content_type

    if content_type not in ALLOWED_AVATAR_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="头像只支持 jpg、png、webp、gif 格式",
        )

    content = await file.read(MAX_AVATAR_SIZE + 1)

    if len(content) > MAX_AVATAR_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="头像文件不能超过 2MB",
        )

    if not is_valid_image_content(content_type, content):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="头像文件内容无效",
        )

    AVATAR_DIR.mkdir(parents=True, exist_ok=True)

    suffix = ALLOWED_AVATAR_TYPES[content_type]
    filename = f"user_{current_user.id}_{uuid4().hex}{suffix}"
    file_path = AVATAR_DIR / filename

    file_path.write_bytes(content)

    current_user.avatar_url = f"/static/images/avatars/{filename}"

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return current_user


def get_user_by_uid(uid: str, db: Session) -> User:
    try:
        user_id = int(uid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )


    return user


@router.get("/{uid}/submissions", response_model=list[UserPublicSubmissionRead])
def list_public_user_submissions(
    uid: str,
    db: Session = Depends(get_db),
):
    user = get_user_by_uid(uid, db)

    statement = (
        select(Submission)
        .where(
            Submission.user_id == user.id,
            Submission.status == "approved",
            Submission.content_deleted.is_(False),
            Submission.content_id.is_not(None),
        )
        .order_by(Submission.created_at.desc(), Submission.id.desc())
    )

    return db.scalars(statement).all()


@router.get("/{uid}", response_model=UserPublicRead)
def get_public_user(
    uid: str,
    db: Session = Depends(get_db),
):
    user = get_user_by_uid(uid, db)

    submission_count = db.scalar(
        select(func.count())
        .select_from(Submission)
        .where(
            Submission.user_id == user.id,
            Submission.status == "approved",
            Submission.content_deleted.is_(False),
            Submission.content_id.is_not(None),
        )
    )

    return UserPublicRead(
        id=user.id,
        uid=f"{user.id:05d}",
        username=user.username,
        avatar_url=user.avatar_url,
        haki_value=user.haki_value,
        created_at=user.created_at,
        submission_count=submission_count or 0,
    )
