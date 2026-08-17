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


router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parents[5]
STORAGE_DIR = PROJECT_ROOT / "storage"
SUBMISSION_DIR = STORAGE_DIR / "uploads" / "submissions"
PUBLISH_HAKI_VALUE = 10


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
            reversal_value = min(PUBLISH_HAKI_VALUE, author.haki_value)
            author.haki_value -= reversal_value

            if reversal_value:
                db.add(
                    HakiRecord(
                        user_id=author.id,
                        change_value=-reversal_value,
                        reason=f"内容被管理员下架：{submission.title}",
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
    delete_submission_file(file_url)


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
