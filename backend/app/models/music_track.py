from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.associations import music_track_characters


class MusicTrack(Base):
    __tablename__ = "music_tracks"

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
        String(160),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    audio_url: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    cover_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    source_type: Mapped[str] = mapped_column(
        String(20),
        default="upload",
        server_default="upload",
        nullable=False,
    )

    duration_seconds: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    character_id: Mapped[int | None] = mapped_column(
        ForeignKey("characters.id"),
        nullable=True,
    )

    original_title: Mapped[str | None] = mapped_column(
        String(160),
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

    author_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    play_count: Mapped[int] = mapped_column(
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
        back_populates="music_tracks",
    )

    characters: Mapped[list["Character"]] = relationship(
        "Character",
        secondary=music_track_characters,
        back_populates="related_music_tracks",
    )

    author: Mapped["User | None"] = relationship(
        "User",
        back_populates="authored_music_tracks",
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
