from pydantic import BaseModel


class ExpenseUploadResponse(BaseModel):
    document_id: int
    job_id: int
