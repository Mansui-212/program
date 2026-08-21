from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.associations import submission_characters


class Submission(Base):
    __tablename__ = "submissions"

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

    submission_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="pending",
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(160),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    file_url: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    source_type: Mapped[str] = mapped_column(
        String(20),
        default="upload",
        server_default="upload",
        nullable=False,
    )

    content_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )

    content_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    cover_url: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    character_id: Mapped[int | None] = mapped_column(
        ForeignKey("characters.id"),
        nullable=True,
    )

    source_name: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    source_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    source_author: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    author_name: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    reject_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    reviewed_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship(
        "User",
        foreign_keys=[user_id],
    )

    reviewer = relationship(
        "User",
        foreign_keys=[reviewed_by],
    )

    character = relationship("Character")

    characters: Mapped[list["Character"]] = relationship(
        "Character",
        secondary=submission_characters,
        back_populates="submissions",
    )

    @property
    def character_ids(self) -> list[int]:
        return [character.id for character in self.characters]

    @property
    def author_uid(self) -> str:
        return f"{self.user_id:05d}"
