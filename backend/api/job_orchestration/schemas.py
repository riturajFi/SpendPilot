from pydantic import BaseModel


class JobRunResponse(BaseModel):
    job_id: int
    status: str
