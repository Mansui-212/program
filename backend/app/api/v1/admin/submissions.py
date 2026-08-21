from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.v1.admin.dependencies import get_current_admin
from app.db.session import get_db
from app.models.meme import Meme
from app.models.music_track import MusicTrack
from app.models.submission import Submission
from app.models.user import User
from app.schemas.admin import AdminSubmissionRead


router = APIRouter()

ALLOWED_SUBMISSION_TYPES = {"meme", "music"}
ALLOWED_SUBMISSION_STATUSES = {"approved", "pending", "rejected"}


@router.get("", response_model=list[AdminSubmissionRead])
def list_admin_submissions(
    submission_type: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if submission_type and submission_type not in ALLOWED_SUBMISSION_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="投稿类型无效",
        )

    if status_filter and status_filter not in ALLOWED_SUBMISSION_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="投稿状态无效",
        )

    statement = (
        select(Submission)
        .options(selectinload(Submission.user), selectinload(Submission.characters))
        .order_by(Submission.created_at.desc(), Submission.id.desc())
        .offset(offset)
        .limit(limit)
    )

    if submission_type:
        statement = statement.where(Submission.submission_type == submission_type)

    if status_filter:
        statement = statement.where(Submission.status == status_filter)

    submissions = db.scalars(statement).all()

    meme_ids = [
        item.content_id
        for item in submissions
        if item.submission_type == "meme" and item.content_id is not None
    ]
    music_ids = [
        item.content_id
        for item in submissions
        if item.submission_type == "music" and item.content_id is not None
    ]
    meme_featured = {
        item.id: item.is_featured
        for item in db.scalars(select(Meme).where(Meme.id.in_(meme_ids))).all()
    } if meme_ids else {}
    music_featured = {
        item.id: item.is_featured
        for item in db.scalars(select(MusicTrack).where(MusicTrack.id.in_(music_ids))).all()
    } if music_ids else {}

    for item in submissions:
        item.content_is_featured = (
            meme_featured.get(item.content_id, False)
            if item.submission_type == "meme"
            else music_featured.get(item.content_id, False)
        )

    return submissions
