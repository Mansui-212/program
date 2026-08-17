from sqlalchemy import Column, ForeignKey, Integer, Table

from app.db.base import Base


submission_characters = Table(
    "submission_characters",
    Base.metadata,
    Column("submission_id", ForeignKey("submissions.id", ondelete="CASCADE"), primary_key=True),
    Column("character_id", ForeignKey("characters.id", ondelete="CASCADE"), primary_key=True),
)

meme_characters = Table(
    "meme_characters",
    Base.metadata,
    Column("meme_id", ForeignKey("memes.id", ondelete="CASCADE"), primary_key=True),
    Column("character_id", ForeignKey("characters.id", ondelete="CASCADE"), primary_key=True),
)

music_track_characters = Table(
    "music_track_characters",
    Base.metadata,
    Column("music_track_id", ForeignKey("music_tracks.id", ondelete="CASCADE"), primary_key=True),
    Column("character_id", ForeignKey("characters.id", ondelete="CASCADE"), primary_key=True),
)
