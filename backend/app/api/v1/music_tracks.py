from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.db.session import get_db
from app.models.associations import music_track_characters
from app.models.character import Character
from app.models.music_track import MusicTrack
from app.schemas.music_track import MusicTrackDetailRead, MusicTrackRead


router = APIRouter()


@router.get("", response_model=list[MusicTrackRead])
def list_music_tracks(
    db: Session = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    character_slug: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
    order: Literal["latest", "featured", "popular"] = Query(default="latest"),
):
    statement = select(MusicTrack).options(
        joinedload(MusicTrack.author),
        selectinload(MusicTrack.characters),
    )

    if character_slug:
        character_id = db.scalar(
            select(Character.id).where(Character.slug == character_slug)
        )

        if character_id is None:
            return []

        statement = (
            statement.outerjoin(
                music_track_characters,
                MusicTrack.id == music_track_characters.c.music_track_id,
            )
            .where(
                or_(
                    MusicTrack.character_id == character_id,
                    music_track_characters.c.character_id == character_id,
                )
            )
            .distinct()
        )

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
        .where(MusicTrack.is_featured.is_(True))
        .order_by(MusicTrack.sort_order.asc(), MusicTrack.id.desc())
        .limit(limit)
    )

    return db.scalars(statement).all()


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
        .where(MusicTrack.slug == slug)
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
