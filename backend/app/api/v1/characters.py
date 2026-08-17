from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.associations import meme_characters, music_track_characters
from app.models.character import Character
from app.models.meme import Meme
from app.models.music_track import MusicTrack
from app.schemas.character import CharacterDetailRead, CharacterRead
from app.schemas.meme import MemeRead
from app.schemas.music_track import MusicTrackRead

router = APIRouter()


@router.get("", response_model=list[CharacterRead])
def list_characters(db: Session = Depends(get_db)):
    statement = select(Character).order_by(Character.sort_order.asc(), Character.id.asc())

    return db.scalars(statement).all()


@router.get("/featured", response_model=list[CharacterRead])
def list_featured_characters(db: Session = Depends(get_db)):
    statement = (
        select(Character)
        .where(Character.is_featured.is_(True))
        .order_by(Character.sort_order.asc(), Character.id.asc())
    )

    return db.scalars(statement).all()


@router.get("/{character_id}/memes", response_model=list[MemeRead])
def list_character_memes(
    character_id: int,
    db: Session = Depends(get_db),
):
    if db.get(Character, character_id) is None:
        raise HTTPException(
            status_code=404,
            detail="角色不存在",
        )

    statement = (
        select(Meme)
        .outerjoin(meme_characters, Meme.id == meme_characters.c.meme_id)
        .options(selectinload(Meme.characters))
        .where(
            or_(
                Meme.character_id == character_id,
                meme_characters.c.character_id == character_id,
            )
        )
        .distinct()
        .order_by(Meme.sort_order.asc(), Meme.id.desc())
    )

    return db.scalars(statement).all()


@router.get("/{character_id}/music", response_model=list[MusicTrackRead])
def list_character_music_tracks(
    character_id: int,
    db: Session = Depends(get_db),
):
    if db.get(Character, character_id) is None:
        raise HTTPException(
            status_code=404,
            detail="角色不存在",
        )

    statement = (
        select(MusicTrack)
        .outerjoin(
            music_track_characters,
            MusicTrack.id == music_track_characters.c.music_track_id,
        )
        .options(selectinload(MusicTrack.characters))
        .where(
            or_(
                MusicTrack.character_id == character_id,
                music_track_characters.c.character_id == character_id,
            )
        )
        .distinct()
        .order_by(MusicTrack.sort_order.asc(), MusicTrack.id.desc())
    )

    return db.scalars(statement).all()


@router.get("/{slug}", response_model=CharacterDetailRead)
def get_character_detail(
    slug: str,
    db: Session = Depends(get_db),
):
    character = db.scalar(
        select(Character).where(Character.slug == slug)
    )

    if character is None:
        raise HTTPException(
            status_code=404,
            detail="角色不存在",
        )

    return character
