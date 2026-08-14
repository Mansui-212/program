from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CharacterRead(BaseModel):
    id: int
    slug: str
    name: str
    aliases: str | None = None
    description: str | None = None
    avatar_url: str | None = None
    theme_color: str | None = None
    sort_order: int
    is_featured: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
