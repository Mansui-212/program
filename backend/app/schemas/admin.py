from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.submission import SubmissionRead


class AdminUserRead(BaseModel):
    id: int
    username: str
    avatar_url: str | None = None
    haki_value: int
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminSubmissionRead(SubmissionRead):
    user: AdminUserRead
    content_is_featured: bool = False

    model_config = ConfigDict(from_attributes=True)


class HakiRecordRead(BaseModel):
    id: int
    user_id: int
    change_value: int
    reason: str
    action: str | None = None
    target_type: str | None = None
    target_id: int | None = None
    source_user_id: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HakiAdjustRequest(BaseModel):
    change_value: int = Field(ge=-10_000, le=10_000)
    reason: str = Field(min_length=1, max_length=255)


class ContentFeaturedUpdate(BaseModel):
    is_featured: bool


class ContentFeaturedRead(BaseModel):
    id: int
    content_type: str
    is_featured: bool


class ContentStatusUpdate(BaseModel):
    status: Literal["active", "removed"]


class ContentStatusRead(BaseModel):
    id: int
    content_type: str
    status: Literal["active", "withdrawn", "removed"]


class AdminOverviewRead(BaseModel):
    total_uploads: int
    published_contents: int
    user_count: int
    total_haki_value: int
