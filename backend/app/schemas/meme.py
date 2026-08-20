from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MemeCharacterRead(BaseModel):
    id: int
    slug: str
    name: str
    avatar_url: str | None = None
    theme_color: str | None = None

    model_config = ConfigDict(from_attributes=True)


class MemeRead(BaseModel):
    id: int
    slug: str
    title: str
    description: str | None = None
    image_url: str
    file_type: str
    character_id: int | None = None
    character_ids: list[int] = []
    source_name: str | None = None
    source_url: str | None = None
    author_name: str | None = None
    author_id: int | None = None
    author_uid: str | None = None
    view_count: int
    download_count: int
    sort_order: int
    is_featured: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MemeDetailRead(MemeRead):
    character: MemeCharacterRead | None = None
