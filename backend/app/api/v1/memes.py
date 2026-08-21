from pathlib import Path
import re
from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload

from app.api.v1.admin.dependencies import get_current_admin
from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.associations import meme_characters
from app.models.character import Character
from app.models.meme import Meme
from app.models.user import User
from app.schemas.meme import BatchMemeUploadRead, MemeDetailRead, MemeRead
from app.services.batch_upload import (
    MAX_BATCH_ARCHIVE_SIZE,
    MAX_BATCH_FILES,
    MAX_BATCH_IMAGE_SIZE,
    MAX_BATCH_TOTAL_SIZE,
    BatchImage,
    BatchUploadError,
    collect_batch_images,
    is_zip_filename,
)
from app.services.haki import add_haki, get_haki_rule_value


router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parents[4]
STORAGE_DIR = PROJECT_ROOT / "storage"
MEME_DIR = STORAGE_DIR / "images" / "memes"


def clean_optional(value: str | None) -> str | None:
    if value is None:
        return None

    return value.strip() or None


def make_batch_meme_title(filename: str, character_name: str, index: int) -> str:
    stem = Path(filename).stem
    title = re.sub(r"[_-]+", " ", stem).strip()
    title = re.sub(r"\s+", " ", title)

    return (title or f"{character_name}表情 {index}")[:120]


def save_batch_meme_image(image: BatchImage) -> tuple[str, Path]:
    MEME_DIR.mkdir(parents=True, exist_ok=True)
    file_path = MEME_DIR / f"batch_{uuid4().hex}{image.suffix}"
    file_path.write_bytes(image.content)

    return f"/static/images/memes/{file_path.name}", file_path


async def read_batch_upload_files(files: list[UploadFile]) -> list[tuple[str, bytes]]:
    if len(files) > MAX_BATCH_FILES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="单次最多选择 500 个文件",
        )

    uploaded_files: list[tuple[str, bytes]] = []
    total_size = 0

    for file in files:
        filename = Path(file.filename or "未命名文件").name
        is_zip = is_zip_filename(filename) or file.content_type in {
            "application/zip",
            "application/x-zip-compressed",
        }
        size_limit = MAX_BATCH_ARCHIVE_SIZE if is_zip else MAX_BATCH_IMAGE_SIZE

        try:
            content = await file.read(size_limit + 1)
        finally:
            await file.close()

        if len(content) > size_limit:
            label = "ZIP 压缩包" if is_zip else "图片文件"
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"{label}不能超过 {size_limit // (1024 * 1024)}MB",
            )

        if not content:
            continue

        total_size += len(content)
        if total_size > MAX_BATCH_TOTAL_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="单次上传文件总大小不能超过 100MB",
            )

        uploaded_files.append((filename, content))

    return uploaded_files


@router.get("", response_model=list[MemeRead])
def list_memes(
    db: Session = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    character_slug: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
    order: Literal["latest", "featured", "popular"] = Query(default="latest"),
):
    statement = select(Meme).options(
        joinedload(Meme.author),
        selectinload(Meme.characters),
    ).where(Meme.status == "active")

    if character_slug:
        character_id = db.scalar(
            select(Character.id).where(Character.slug == character_slug)
        )

        if character_id is None:
            return []

        statement = (
            statement.outerjoin(meme_characters, Meme.id == meme_characters.c.meme_id)
            .where(
                or_(
                    Meme.character_id == character_id,
                    meme_characters.c.character_id == character_id,
                )
            )
            .distinct()
        )

    if keyword:
        like_keyword = f"%{keyword}%"
        statement = statement.where(Meme.title.like(like_keyword))

    if order == "featured":
        statement = statement.order_by(Meme.sort_order.asc(), Meme.id.desc())
    elif order == "popular":
        statement = statement.order_by(Meme.view_count.desc(), Meme.id.desc())
    else:
        statement = statement.order_by(Meme.created_at.desc(), Meme.id.desc())

    statement = statement.offset(offset).limit(limit)

    return db.scalars(statement).all()


@router.get("/latest", response_model=list[MemeRead])
def list_latest_memes(
    db: Session = Depends(get_db),
    limit: int = Query(default=8, ge=1, le=50),
):
    statement = (
        select(Meme)
        .options(joinedload(Meme.author), selectinload(Meme.characters))
        .where(Meme.status == "active")
        .order_by(Meme.created_at.desc(), Meme.id.desc())
        .limit(limit)
    )

    return db.scalars(statement).all()


@router.get("/featured", response_model=list[MemeRead])
def list_featured_memes(
    db: Session = Depends(get_db),
    limit: int = Query(default=8, ge=1, le=50),
):
    statement = (
        select(Meme)
        .options(joinedload(Meme.author), selectinload(Meme.characters))
        .where(Meme.status == "active", Meme.is_featured.is_(True))
        .order_by(Meme.sort_order.asc(), Meme.id.desc())
        .limit(limit)
    )

    return db.scalars(statement).all()


@router.post(
    "/batch-upload",
    response_model=BatchMemeUploadRead,
    status_code=status.HTTP_201_CREATED,
)
async def batch_upload_memes(
    files: list[UploadFile] = File(...),
    character_id: int = Form(...),
    source_name: str | None = Form(default=None),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Import image files or a ZIP archive into the meme library for one character."""
    character = db.get(Character, character_id)
    if character is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="关联角色不存在",
        )

    cleaned_source_name = clean_optional(source_name)
    if cleaned_source_name and len(cleaned_source_name) > 120:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="来源名称不能超过 120 个字符",
        )

    uploaded_files = await read_batch_upload_files(files)
    if not uploaded_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请选择至少一个图片文件或 ZIP 压缩包",
        )

    try:
        collection = collect_batch_images(uploaded_files)
    except BatchUploadError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    image_hashes = [image.image_hash for image in collection.images]
    existing_hashes = set(
        db.scalars(
            select(Meme.image_hash).where(Meme.image_hash.in_(image_hashes))
        ).all()
    ) if image_hashes else set()

    items = [
        {
            "filename": item.filename,
            "status": "invalid",
            "detail": item.detail,
        }
        for item in collection.skipped
    ]
    seen_hashes = set(existing_hashes)
    written_files: list[Path] = []
    imported = 0
    skipped_duplicates = 0

    try:
        for image in collection.images:
            if image.image_hash in seen_hashes:
                skipped_duplicates += 1
                items.append(
                    {
                        "filename": image.filename,
                        "status": "duplicate",
                        "detail": "内容相同的图片已在表情包库中",
                    }
                )
                continue

            seen_hashes.add(image.image_hash)
            image_url, file_path = save_batch_meme_image(image)
            written_files.append(file_path)

            imported += 1
            title = make_batch_meme_title(image.filename, character.name, imported)
            meme = Meme(
                slug=f"batch-meme-{uuid4().hex}",
                title=title,
                image_url=image_url,
                image_hash=image.image_hash,
                file_type="gif" if image.content_type == "image/gif" else "image",
                character_id=character.id,
                characters=[character],
                source_name=cleaned_source_name or "管理员批量导入",
                author_name=current_user.username,
                author_id=current_user.id,
                is_featured=False,
            )
            db.add(meme)
            items.append(
                {
                    "filename": image.filename,
                    "status": "imported",
                    "title": title,
                }
            )

        haki_gained = 0
        if imported:
            per_image_value = max(get_haki_rule_value(db, "batch_upload"), 0)
            haki_gained = min(imported * per_image_value, 100)
            add_haki(
                db,
                current_user,
                "batch_upload",
                target_type="meme",
                reason=f"批量导入 {imported} 张表情包",
                value=haki_gained,
            )

        db.commit()
    except IntegrityError as error:
        db.rollback()
        for file_path in written_files:
            file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="导入时检测到重复图片，请重新上传其余文件",
        ) from error
    except Exception:
        db.rollback()
        for file_path in written_files:
            file_path.unlink(missing_ok=True)
        raise

    return {
        "total_candidates": len(collection.images) + len(collection.skipped),
        "imported": imported,
        "skipped_duplicates": skipped_duplicates,
        "skipped_invalid": len(collection.skipped),
        "haki_gained": haki_gained,
        "items": items,
    }


@router.delete("/{meme_id}/withdraw")
def withdraw_meme(
    meme_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    meme = db.get(Meme, meme_id)

    if meme is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="表情包不存在",
        )

    if meme.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="不能撤回其他用户的作品",
        )

    if meme.status != "active":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该表情包已撤回或下架",
        )

    meme.status = "withdrawn"
    meme.is_featured = False
    db.commit()

    return {"message": "表情包已撤回"}


@router.get("/{slug}", response_model=MemeDetailRead)
def get_meme_detail(
    slug: str,
    db: Session = Depends(get_db),
):
    statement = (
        select(Meme)
        .options(
            joinedload(Meme.author),
            selectinload(Meme.character),
            selectinload(Meme.characters),
        )
        .where(Meme.slug == slug, Meme.status == "active")
    )

    meme = db.scalars(statement).first()

    if meme is None:
        raise HTTPException(
            status_code=404,
            detail="表情包不存在",
        )

    meme.view_count += 1
    db.commit()
    db.refresh(meme)

    return meme
