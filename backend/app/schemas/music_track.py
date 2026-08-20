from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MusicTrackCharacterRead(BaseModel):
    id: int
    slug: str
    name: str
    avatar_url: str | None = None
    theme_color: str | None = None

    model_config = ConfigDict(from_attributes=True)


class MusicTrackRead(BaseModel):
    id: int
    slug: str
    title: str
    description: str | None = None
    audio_url: str
    cover_url: str | None = None
    duration_seconds: int | None = None
    character_id: int | None = None
    character_ids: list[int] = []
    original_title: str | None = None
    source_name: str | None = None
    source_url: str | None = None
    author_name: str | None = None
    author_id: int | None = None
    author_uid: str | None = None
    play_count: int
    sort_order: int
    is_featured: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MusicTrackDetailRead(MusicTrackRead):
    character: MusicTrackCharacterRead | None = None
