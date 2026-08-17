from datetime import datetime

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

    model_config = ConfigDict(from_attributes=True)


class HakiRecordRead(BaseModel):
    id: int
    user_id: int
    change_value: int
    reason: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HakiAdjustRequest(BaseModel):
    change_value: int = Field(ge=-10_000, le=10_000)
    reason: str = Field(min_length=1, max_length=255)


class AdminOverviewRead(BaseModel):
    total_uploads: int
    published_contents: int
    user_count: int
    total_haki_value: int
