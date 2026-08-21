from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import case, or_, select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.character import Character
from app.models.meme import Meme
from app.models.music_track import MusicTrack
from app.schemas.search import SearchRead


router = APIRouter()

SearchPrimaryType = Literal["characters", "memes", "music", "none"]


def get_search_term(query: str) -> tuple[str, SearchPrimaryType | None]:
    """Extract a lightweight content hint while retaining normal LIKE search."""
    normalized = query.strip()
    lowered = normalized.lower()

    music_terms = ("音乐", "歌曲", "音频", "mp3", "music")
    meme_terms = ("表情包", "表情", "动图", "图片", "gif", "meme")

    for term in music_terms:
        if term in lowered:
            search_term = normalized.replace(term, "").strip()
            return search_term or normalized, "music"

    for term in meme_terms:
        if term in lowered:
            search_term = normalized.replace(term, "").strip()
            return search_term or normalized, "memes"

    return normalized, None


@router.get("", response_model=SearchRead)
def search_site(
    q: str = Query(..., min_length=1, max_length=100),
    db: Session = Depends(get_db),
):
    query = q.strip()

    if not query:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="搜索关键词不能为空",
        )

    search_term, requested_type = get_search_term(query)
    like_keyword = f"%{search_term}%"

    characters = db.scalars(
        select(Character)
        .where(
            or_(
                Character.name.like(like_keyword),
                Character.aliases.like(like_keyword),
                Character.description.like(like_keyword),
                Character.origin_story.like(like_keyword),
            )
        )
        .order_by(
            case(
                (Character.name.like(like_keyword), 0),
                (Character.aliases.like(like_keyword), 1),
                (Character.description.like(like_keyword), 2),
                else_=3,
            ),
            Character.sort_order.asc(),
            Character.id.asc(),
        )
        .limit(10)
    ).all()

    memes = db.scalars(
        select(Meme)
        .options(selectinload(Meme.characters))
        .where(
            Meme.status == "active",
            or_(
                Meme.title.like(like_keyword),
                Meme.description.like(like_keyword),
            )
        )
        .order_by(
            case(
                (Meme.title.like(like_keyword), 0),
                else_=1,
            ),
            Meme.created_at.desc(),
            Meme.id.desc(),
        )
        .limit(20)
    ).all()

    music = db.scalars(
        select(MusicTrack)
        .options(selectinload(MusicTrack.characters))
        .where(
            MusicTrack.status == "active",
            or_(
                MusicTrack.title.like(like_keyword),
                MusicTrack.description.like(like_keyword),
                MusicTrack.original_title.like(like_keyword),
            )
        )
        .order_by(
            case(
                (MusicTrack.title.like(like_keyword), 0),
                else_=1,
            ),
            MusicTrack.created_at.desc(),
            MusicTrack.id.desc(),
        )
        .limit(20)
    ).all()

    if requested_type == "music" and music:
        primary_type: SearchPrimaryType = "music"
    elif requested_type == "memes" and memes:
        primary_type = "memes"
    elif characters:
        primary_type = "characters"
    elif memes:
        primary_type = "memes"
    elif music:
        primary_type = "music"
    else:
        primary_type = "none"

    return {
        "keyword": query,
        "primary_type": primary_type,
        "characters": characters,
        "memes": memes,
        "music": music,
    }
