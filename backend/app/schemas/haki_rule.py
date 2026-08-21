from pydantic import BaseModel, Field


class HakiRuleRead(BaseModel):
    id: int
    action: str
    value: int


class HakiRuleUpdate(BaseModel):
    value: int = Field(ge=-10_000, le=10_000)
