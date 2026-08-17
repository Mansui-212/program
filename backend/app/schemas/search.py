from typing import Literal

from pydantic import BaseModel

from app.schemas.character import CharacterDetailRead
from app.schemas.meme import MemeRead
from app.schemas.music_track import MusicTrackRead


class SearchRead(BaseModel):
    keyword: str
    primary_type: Literal["characters", "memes", "music", "none"]
    characters: list[CharacterDetailRead]
    memes: list[MemeRead]
    music: list[MusicTrackRead]
