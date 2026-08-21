from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


TargetType = Literal["meme", "music"]


class FavoriteCreate(BaseModel):
    target_type: TargetType
    target_id: int = Field(ge=1)


class FavoriteStatusRead(BaseModel):
    target_type: TargetType
    target_id: int
    is_favorited: bool


class FavoriteRead(BaseModel):
    id: int
    target_type: TargetType
    target_id: int
    title: str
    description: str | None = None
    image_url: str | None = None
    audio_url: str | None = None
    cover_url: str | None = None
    author_name: str | None = None
    created_at: datetime
