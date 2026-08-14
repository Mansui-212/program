from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MemeRead(BaseModel):
    id: int
    slug: str
    title: str
    description: str | None = None
    image_url: str
    file_type: str
    character_id: int | None = None
    source_name: str | None = None
    source_url: str | None = None
    author_name: str | None = None
    view_count: int
    download_count: int
    sort_order: int
    is_featured: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
