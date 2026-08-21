from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.meme import Meme
from app.models.music_track import MusicTrack
from app.models.submission import Submission


def populate_submission_content_statuses(
    db: Session,
    submissions: Iterable[Submission],
) -> None:
    """Attach the current public-content state to submission history records."""
    submission_list = list(submissions)
    meme_ids = [
        item.content_id
        for item in submission_list
        if item.submission_type == "meme" and item.content_id is not None
    ]
    music_ids = [
        item.content_id
        for item in submission_list
        if item.submission_type == "music" and item.content_id is not None
    ]

    meme_statuses = {
        item.id: item.status
        for item in db.scalars(select(Meme).where(Meme.id.in_(meme_ids))).all()
    } if meme_ids else {}
    music_statuses = {
        item.id: item.status
        for item in db.scalars(select(MusicTrack).where(MusicTrack.id.in_(music_ids))).all()
    } if music_ids else {}

    for item in submission_list:
        if item.content_deleted or item.content_id is None:
            item.content_status = "removed"
        elif item.submission_type == "meme":
            item.content_status = meme_statuses.get(item.content_id, "removed")
        else:
            item.content_status = music_statuses.get(item.content_id, "removed")
