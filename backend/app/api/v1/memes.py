from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.db.session import get_db
from app.models.associations import meme_characters
from app.models.character import Character
from app.models.meme import Meme
from app.schemas.meme import MemeDetailRead, MemeRead


router = APIRouter()


@router.get("", response_model=list[MemeRead])
def list_memes(
    db: Session = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    character_slug: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
    order: Literal["latest", "featured", "popular"] = Query(default="latest"),
):
    statement = select(Meme).options(
        joinedload(Meme.author),
        selectinload(Meme.characters),
    )

    if character_slug:
        character_id = db.scalar(
            select(Character.id).where(Character.slug == character_slug)
        )

        if character_id is None:
            return []

        statement = (
            statement.outerjoin(meme_characters, Meme.id == meme_characters.c.meme_id)
            .where(
                or_(
                    Meme.character_id == character_id,
                    meme_characters.c.character_id == character_id,
                )
            )
            .distinct()
        )

    if keyword:
        like_keyword = f"%{keyword}%"
        statement = statement.where(Meme.title.like(like_keyword))

    if order == "featured":
        statement = statement.order_by(Meme.sort_order.asc(), Meme.id.desc())
    elif order == "popular":
        statement = statement.order_by(Meme.view_count.desc(), Meme.id.desc())
    else:
        statement = statement.order_by(Meme.created_at.desc(), Meme.id.desc())

    statement = statement.offset(offset).limit(limit)

    return db.scalars(statement).all()


@router.get("/latest", response_model=list[MemeRead])
def list_latest_memes(
    db: Session = Depends(get_db),
    limit: int = Query(default=8, ge=1, le=50),
):
    statement = (
        select(Meme)
        .options(joinedload(Meme.author), selectinload(Meme.characters))
        .order_by(Meme.created_at.desc(), Meme.id.desc())
        .limit(limit)
    )

    return db.scalars(statement).all()


@router.get("/featured", response_model=list[MemeRead])
def list_featured_memes(
    db: Session = Depends(get_db),
    limit: int = Query(default=8, ge=1, le=50),
):
    statement = (
        select(Meme)
        .options(joinedload(Meme.author), selectinload(Meme.characters))
        .where(Meme.is_featured.is_(True))
        .order_by(Meme.sort_order.asc(), Meme.id.desc())
        .limit(limit)
    )

    return db.scalars(statement).all()


@router.get("/{slug}", response_model=MemeDetailRead)
def get_meme_detail(
    slug: str,
    db: Session = Depends(get_db),
):
    statement = (
        select(Meme)
        .options(
            joinedload(Meme.author),
            selectinload(Meme.character),
            selectinload(Meme.characters),
        )
        .where(Meme.slug == slug)
    )

    meme = db.scalars(statement).first()

    if meme is None:
        raise HTTPException(
            status_code=404,
            detail="表情包不存在",
        )

    meme.view_count += 1
    db.commit()
    db.refresh(meme)

    return meme
