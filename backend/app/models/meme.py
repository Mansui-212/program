from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.associations import meme_characters


class Meme(Base):
    __tablename__ = "memes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    slug: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        index=True,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    image_url: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    file_type: Mapped[str] = mapped_column(
        String(20),
        default="image",
        nullable=False,
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
        String(255),
        nullable=True,
    )

    author_name: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    author_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    view_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    download_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    is_featured: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
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

    character: Mapped["Character | None"] = relationship(
        "Character",
        back_populates="memes",
    )

    characters: Mapped[list["Character"]] = relationship(
        "Character",
        secondary=meme_characters,
        back_populates="related_memes",
    )

    author: Mapped["User | None"] = relationship(
        "User",
        back_populates="authored_memes",
        foreign_keys=[author_id],
    )

    @property
    def character_ids(self) -> list[int]:
        return [character.id for character in self.characters]

    @property
    def author_uid(self) -> str | None:
        if self.author_id is None:
            return None

        return f"{self.author_id:05d}"
