from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChronicleEventRead(BaseModel):
    id: int
    year: int
    date: str | None = None
    title: str
    content: str
    image_url: str | None = None
    sort_order: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChronicleEventCreate(BaseModel):
    year: int = Field(ge=2000, le=2100)
    date: str | None = Field(default=None, max_length=50)
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    image_url: str | None = Field(default=None, max_length=500)
    sort_order: int = 0


class ChronicleEventUpdate(BaseModel):
    year: int | None = Field(default=None, ge=2000, le=2100)
    date: str | None = Field(default=None, max_length=50)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1)
    image_url: str | None = Field(default=None, max_length=500)
    sort_order: int | None = None
