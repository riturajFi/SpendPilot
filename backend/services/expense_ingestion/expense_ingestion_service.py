from logging import getLogger
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.repositories import DocumentRepository, JobRepository
from backend.services.expense_ingestion.storage import RawArtifactStore
from backend.services.expense_pipeline_statuses import (
    DOCUMENT_STATUS_UPLOADED,
    JOB_STATUS_PENDING,
)

logger = getLogger(__name__)


class ExpenseIngestionService:
    def __init__(
        self,
        session: Session,
        artifact_store: RawArtifactStore,
        document_repo: DocumentRepository,
        job_repo: JobRepository,
    ) -> None:
        self.session = session
        self.artifact_store = artifact_store
        self.document_repo = document_repo
        self.job_repo = job_repo

    def ingest_file(self, file_bytes: bytes, file_name: str) -> dict:
        self._validate_uploaded_file(file_bytes=file_bytes, file_name=file_name)
        file_type = self._get_file_type(file_name)

        try:
            logger.info("Expense ingestion start file_name=%s", file_name)
            file_key = self.artifact_store.save_file(file_bytes, file_name)
            document = self.document_repo.create(
                file_key=file_key,
                file_type=file_type,
                status=DOCUMENT_STATUS_UPLOADED,
            )
            job = self.job_repo.create(
                document_id=document.id,
                status=JOB_STATUS_PENDING,
            )
            self.session.commit()
            logger.info(
                "Expense ingestion success document_id=%s job_id=%s",
                document.id,
                job.id,
            )
        except Exception:
            self.session.rollback()
            logger.exception("Expense ingestion failed file_name=%s", file_name)
            raise

        return {
            "document_id": document.id,
            "job_id": job.id,
        }

    def _validate_uploaded_file(self, file_bytes: bytes, file_name: str) -> None:
        if not file_name or not file_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is required",
            )

    def _get_file_type(self, file_name: str) -> str:
        file_type = Path(file_name).suffix.lstrip(".").lower()
        if not file_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file must have an extension",
            )
        return file_type
