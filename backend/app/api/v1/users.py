from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserRead


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
