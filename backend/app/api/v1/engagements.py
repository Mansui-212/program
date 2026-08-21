from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.api.v1.favorites import get_target
from app.db.session import get_db
from app.models.haki_record import HakiRecord
from app.models.meme import Meme
from app.models.user import User
from app.schemas.favorite import FavoriteCreate
from app.services.haki import add_haki


router = APIRouter()


@router.post("/downloads")
def record_download(
    data: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target = get_target(db, data.target_type, data.target_id)

    if isinstance(target, Meme):
        target.download_count += 1

    reward_granted = False
    if target.author_id is not None and target.author_id != current_user.id:
        rewarded = db.scalar(
            select(HakiRecord.id).where(
                HakiRecord.user_id == target.author_id,
                HakiRecord.action == "download_get",
                HakiRecord.target_type == data.target_type,
                HakiRecord.target_id == target.id,
                HakiRecord.source_user_id == current_user.id,
            )
        )
        author = db.get(User, target.author_id)
        if rewarded is None and author is not None:
            add_haki(
                db,
                author,
                "download_get",
                target_type=data.target_type,
                target_id=target.id,
                source_user_id=current_user.id,
            )
            reward_granted = True

    db.commit()
    return {"ok": True, "author_reward_granted": reward_granted}
