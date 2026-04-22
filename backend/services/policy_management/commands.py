from pydantic import BaseModel, ConfigDict, Field


class CreatePolicyCommand(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)


class UpdatePolicyCommand(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    policy_id: int
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)


class DeletePolicyCommand(BaseModel):
    policy_id: int
