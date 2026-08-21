from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.api.v1.admin.dependencies import get_current_admin
from app.db.session import get_db
from app.models.haki_record import HakiRecord
from app.models.meme import Meme
from app.models.music_track import MusicTrack
from app.models.submission import Submission
from app.models.user import User
from app.schemas.admin import ContentFeaturedRead, ContentFeaturedUpdate
from app.services.haki import add_haki


router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parents[5]
STORAGE_DIR = PROJECT_ROOT / "storage"
SUBMISSION_DIR = STORAGE_DIR / "uploads" / "submissions"
def delete_submission_file(file_url: str) -> None:
    static_prefix = "/static/"

    if not file_url.startswith(static_prefix):
        return

    file_path = (STORAGE_DIR / file_url.removeprefix(static_prefix)).resolve()

    try:
        file_path.relative_to(SUBMISSION_DIR.resolve())
    except ValueError:
        return

    if file_path.is_file():
        file_path.unlink()


def delete_content(
    *,
    content: Meme | MusicTrack,
    content_type: str,
    db: Session,
) -> None:
    file_url = content.image_url if isinstance(content, Meme) else content.audio_url
    submissions = db.scalars(
        select(Submission).where(
            Submission.submission_type == content_type,
            Submission.content_id == content.id,
            Submission.content_deleted.is_(False),
        )
    ).all()

    for submission in submissions:
        author = db.get(User, submission.user_id)

        if author is not None:
            upload_action = "upload_meme" if content_type == "meme" else "upload_music"
            upload_value = db.scalar(
                select(HakiRecord.change_value)
                .where(
                    HakiRecord.user_id == author.id,
                    HakiRecord.action == upload_action,
                    HakiRecord.target_type == content_type,
                    HakiRecord.target_id == content.id,
                )
                .order_by(HakiRecord.id.desc())
            )
            reversal_value = min(upload_value or 10, author.haki_value)
            author.haki_value -= reversal_value

            if reversal_value:
                db.add(
                    HakiRecord(
                        user_id=author.id,
                        change_value=-reversal_value,
                        reason=f"内容被管理员下架：{submission.title}",
                        action="content_removed",
                        target_type=content_type,
                        target_id=content.id,
                    )
                )

    db.execute(
        update(Submission)
        .where(
            Submission.submission_type == content_type,
            Submission.content_id == content.id,
        )
        .values(content_deleted=True)
    )
    db.delete(content)
    db.commit()


@router.put(
    "/{content_type}/{content_id}/featured",
    response_model=ContentFeaturedRead,
)
def update_content_featured(
    content_type: str,
    content_id: int,
    data: ContentFeaturedUpdate,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if content_type == "meme":
        content = db.get(Meme, content_id)
    elif content_type == "music":
        content = db.get(MusicTrack, content_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="内容类型无效",
        )

    if content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="内容不存在",
        )

    was_featured = content.is_featured
    content.is_featured = data.is_featured

    if data.is_featured and not was_featured and content.author_id is not None:
        already_rewarded = db.scalar(
            select(HakiRecord.id).where(
                HakiRecord.user_id == content.author_id,
                HakiRecord.action == "admin_pick",
                HakiRecord.target_type == content_type,
                HakiRecord.target_id == content.id,
            )
        )
        author = db.get(User, content.author_id)
        if already_rewarded is None and author is not None:
            add_haki(
                db,
                author,
                "admin_pick",
                target_type=content_type,
                target_id=content.id,
            )

    db.commit()
    return ContentFeaturedRead(
        id=content.id,
        content_type=content_type,
        is_featured=content.is_featured,
    )



@router.delete("/memes/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meme(
    content_id: int,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Response:
    meme = db.get(Meme, content_id)

    if meme is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="表情包不存在",
        )

    delete_content(content=meme, content_type="meme", db=db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/music-tracks/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_music_track(
    content_id: int,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Response:
    track = db.get(MusicTrack, content_id)

    if track is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="音乐不存在",
        )

    delete_content(content=track, content_type="music", db=db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
