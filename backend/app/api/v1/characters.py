from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.character import Character
from app.schemas.character import CharacterRead

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
