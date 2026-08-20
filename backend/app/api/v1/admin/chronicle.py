from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.admin.dependencies import get_current_admin
from app.db.session import get_db
from app.models.chronicle_event import ChronicleEvent
from app.models.user import User
from app.schemas.chronicle import ChronicleEventCreate, ChronicleEventRead, ChronicleEventUpdate


router = APIRouter()


@router.get("", response_model=list[ChronicleEventRead])
def list_admin_chronicle_events(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    statement = select(ChronicleEvent).order_by(
        ChronicleEvent.year.asc(),
        ChronicleEvent.date.asc(),
        ChronicleEvent.sort_order.asc(),
        ChronicleEvent.id.asc(),
    )

    return db.scalars(statement).all()


@router.post("", response_model=ChronicleEventRead, status_code=status.HTTP_201_CREATED)
def create_chronicle_event(
    data: ChronicleEventCreate,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    event = ChronicleEvent(**data.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)

    return event


@router.put("/{event_id}", response_model=ChronicleEventRead)
def update_chronicle_event(
    event_id: int,
    data: ChronicleEventUpdate,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    event = db.get(ChronicleEvent, event_id)

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="编年史事件不存在",
        )

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)

    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chronicle_event(
    event_id: int,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Response:
    event = db.get(ChronicleEvent, event_id)

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="编年史事件不存在",
        )

    db.delete(event)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
