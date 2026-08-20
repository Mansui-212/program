from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SubmissionRead(BaseModel):
    id: int
    user_id: int
    submission_type: str
    status: str
    title: str
    description: str | None = None
    file_url: str
    content_id: int | None = None
    content_deleted: bool
    cover_url: str | None = None
    character_id: int | None = None
    character_ids: list[int] = []
    source_name: str | None = None
    source_url: str | None = None
    author_name: str | None = None
    author_uid: str | None = None
    reject_reason: str | None = None
    reviewed_by: int | None = None
    reviewed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
