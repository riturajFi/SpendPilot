from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from backend.api.expense_ingestion.schemas import ExpenseUploadResponse
from backend.dependencies import get_db_session
from backend.repositories import DocumentRepository, JobRepository
from backend.services.expense_ingestion import ExpenseIngestionService, LocalRawArtifactStore


router = APIRouter(prefix="/expenses", tags=["expense-ingestion"])


def get_expense_ingestion_service(
    session: Session = Depends(get_db_session),
) -> ExpenseIngestionService:
    return ExpenseIngestionService(
        session=session,
        artifact_store=LocalRawArtifactStore(),
        document_repo=DocumentRepository(session),
        job_repo=JobRepository(session),
    )


@router.post("/upload", response_model=ExpenseUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_expense(
    file: UploadFile = File(...),
    service: ExpenseIngestionService = Depends(get_expense_ingestion_service),
) -> ExpenseUploadResponse:
    result = service.ingest_file(file_bytes=await file.read(), file_name=file.filename or "")
    return ExpenseUploadResponse(**result)
