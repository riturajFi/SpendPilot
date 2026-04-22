from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreatePolicyRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)


class UpdatePolicyRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)


class PolicyResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
