from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.admin.dependencies import get_current_admin
from app.db.session import get_db
from app.models.haki_record import HakiRecord
from app.models.meme import Meme
from app.models.music_track import MusicTrack
from app.models.user import User
from app.schemas.admin import (
    ContentFeaturedRead,
    ContentFeaturedUpdate,
    ContentStatusRead,
    ContentStatusUpdate,
)
from app.services.haki import add_haki


router = APIRouter()


def get_content(content_type: str, content_id: int, db: Session) -> Meme | MusicTrack:
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

    return content


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
    content = get_content(content_type, content_id, db)

    if content.status != "active":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="已撤回或下架的内容不能设为精选",
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


@router.put(
    "/{content_type}/{content_id}/status",
    response_model=ContentStatusRead,
)
def update_content_status(
    content_type: str,
    content_id: int,
    data: ContentStatusUpdate,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    content = get_content(content_type, content_id, db)
    content.status = data.status

    if data.status != "active":
        content.is_featured = False

    db.commit()
    return ContentStatusRead(
        id=content.id,
        content_type=content_type,
        status=content.status,
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

    meme.status = "removed"
    meme.is_featured = False
    db.commit()
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

    track.status = "removed"
    track.is_featured = False
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
