from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.v1.admin.contents import router as contents_router
from app.api.v1.admin.chronicle import router as chronicle_router
from app.api.v1.admin.dependencies import get_current_admin
from app.api.v1.admin.submissions import router as submissions_router
from app.api.v1.admin.users import router as users_router
from app.db.session import get_db
from app.models.meme import Meme
from app.models.music_track import MusicTrack
from app.models.submission import Submission
from app.models.user import User
from app.schemas.admin import AdminOverviewRead


router = APIRouter()


@router.get("/overview", response_model=AdminOverviewRead)
def get_admin_overview(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    total_uploads = db.scalar(select(func.count(Submission.id))) or 0
    meme_count = db.scalar(select(func.count(Meme.id))) or 0
    music_count = db.scalar(select(func.count(MusicTrack.id))) or 0
    user_count = db.scalar(select(func.count(User.id))) or 0
    total_haki_value = db.scalar(select(func.coalesce(func.sum(User.haki_value), 0))) or 0

    return {
        "total_uploads": total_uploads,
        "published_contents": meme_count + music_count,
        "user_count": user_count,
        "total_haki_value": total_haki_value,
    }


router.include_router(submissions_router, prefix="/submissions", tags=["admin-submissions"])
router.include_router(users_router, prefix="/users", tags=["admin-users"])
router.include_router(contents_router, prefix="/contents", tags=["admin-contents"])
router.include_router(chronicle_router, prefix="/chronicle", tags=["admin-chronicle"])
