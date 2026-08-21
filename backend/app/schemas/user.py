from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserRegister(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=6, max_length=100)


class UserLogin(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    id: int
    username: str
    avatar_url: str | None = None
    haki_value: int
    role: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenRead(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class UserPublicRead(BaseModel):
    id: int
    uid: str
    username: str
    avatar_url: str | None
    haki_value: int
    created_at: datetime
    submission_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class UserPublicSubmissionRead(BaseModel):
    id: int
    submission_type: str
    title: str
    description: str | None = None
    file_url: str
    cover_url: str | None = None
    content_id: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserRankingRead(BaseModel):
    id: int
    uid: str
    username: str
    avatar_url: str | None = None
    haki_value: int
