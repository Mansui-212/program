from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.music_track import MusicTrack
from app.models.user import User
from app.schemas.music_track import MusicTrackDetailRead, MusicTrackRead


router = APIRouter()


@router.get("", response_model=list[MusicTrackRead])
def list_music_tracks(
    db: Session = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    keyword: str | None = Query(default=None),
    order: Literal["latest", "featured", "popular"] = Query(default="latest"),
):
    statement = select(MusicTrack).options(
        joinedload(MusicTrack.author),
        selectinload(MusicTrack.characters),
    ).where(MusicTrack.status == "active")

    if keyword:
        like_keyword = f"%{keyword}%"
        statement = statement.where(MusicTrack.title.like(like_keyword))

    if order == "featured":
        statement = statement.order_by(MusicTrack.sort_order.asc(), MusicTrack.id.desc())
    elif order == "popular":
        statement = statement.order_by(MusicTrack.play_count.desc(), MusicTrack.id.desc())
    else:
        statement = statement.order_by(MusicTrack.created_at.desc(), MusicTrack.id.desc())

    statement = statement.offset(offset).limit(limit)

    return db.scalars(statement).all()


@router.get("/latest", response_model=list[MusicTrackRead])
def list_latest_music_tracks(
    db: Session = Depends(get_db),
    limit: int = Query(default=8, ge=1, le=50),
):
    statement = (
        select(MusicTrack)
        .options(joinedload(MusicTrack.author), selectinload(MusicTrack.characters))
        .where(MusicTrack.status == "active")
        .order_by(MusicTrack.created_at.desc(), MusicTrack.id.desc())
        .limit(limit)
    )

    return db.scalars(statement).all()


@router.get("/featured", response_model=list[MusicTrackRead])
def list_featured_music_tracks(
    db: Session = Depends(get_db),
    limit: int = Query(default=8, ge=1, le=50),
):
    statement = (
        select(MusicTrack)
        .options(joinedload(MusicTrack.author), selectinload(MusicTrack.characters))
        .where(MusicTrack.status == "active", MusicTrack.is_featured.is_(True))
        .order_by(MusicTrack.sort_order.asc(), MusicTrack.id.desc())
        .limit(limit)
    )

    return db.scalars(statement).all()


@router.delete("/{track_id}/withdraw")
def withdraw_music_track(
    track_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    track = db.get(MusicTrack, track_id)

    if track is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="音乐不存在",
        )

    if track.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="不能撤回其他用户的作品",
        )

    if track.status != "active":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该音乐已撤回或下架",
        )

    track.status = "withdrawn"
    track.is_featured = False
    db.commit()

    return {"message": "音乐已撤回"}


@router.get("/{slug}", response_model=MusicTrackDetailRead)
def get_music_track_detail(
    slug: str,
    db: Session = Depends(get_db),
):
    statement = (
        select(MusicTrack)
        .options(
            joinedload(MusicTrack.author),
            selectinload(MusicTrack.character),
            selectinload(MusicTrack.characters),
        )
        .where(MusicTrack.slug == slug, MusicTrack.status == "active")
    )

    track = db.scalars(statement).first()

    if track is None:
        raise HTTPException(
            status_code=404,
            detail="音乐不存在",
        )

    track.play_count += 1
    db.commit()
    db.refresh(track)

    return track
