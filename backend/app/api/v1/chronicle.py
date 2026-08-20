from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.chronicle_event import ChronicleEvent
from app.schemas.chronicle import ChronicleEventRead


router = APIRouter()


@router.get("", response_model=list[ChronicleEventRead])
def list_chronicle_events(
    db: Session = Depends(get_db),
):
    statement = select(ChronicleEvent).order_by(
        ChronicleEvent.year.asc(),
        ChronicleEvent.date.asc(),
        ChronicleEvent.sort_order.asc(),
        ChronicleEvent.id.asc(),
    )

    return db.scalars(statement).all()
