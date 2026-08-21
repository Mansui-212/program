from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class HakiRecord(Base):
    __tablename__ = "haki_records"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    change_value: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    action: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )

    target_type: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    target_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )

    source_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="haki_records",
        foreign_keys=[user_id],
    )

    source_user: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[source_user_id],
    )
