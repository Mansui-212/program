from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.meme import Meme
from app.schemas.meme import MemeRead


router = APIRouter()


@router.get("", response_model=list[MemeRead])
def list_memes(
    db: Session = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100),
):
    statement = (
        select(Meme)
        .order_by(Meme.sort_order.asc(), Meme.id.desc())
        .limit(limit)
    )

    return db.scalars(statement).all()


@router.get("/latest", response_model=list[MemeRead])
def list_latest_memes(
    db: Session = Depends(get_db),
    limit: int = Query(default=8, ge=1, le=50),
):
    statement = (
        select(Meme)
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
        .where(Meme.is_featured.is_(True))
        .order_by(Meme.sort_order.asc(), Meme.id.desc())
        .limit(limit)
    )

    return db.scalars(statement).all()
