from logging import getLogger

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.repositories import JobRepository
from backend.services.expense_pipeline_statuses import (
    JOB_STATUS_COMPLETED,
    JOB_STATUS_FAILED,
    JOB_STATUS_RUNNING,
)
from backend.services.job_orchestration.contracts import (
    ApprovalWorkflowStep,
    DocumentParsingStep,
    ExpenseExtractionStep,
    PolicyEvaluationStep,
    PolicyRetrievalStep,
    RiskCheckStep,
)

logger = getLogger(__name__)


class JobOrchestrationService:
    def __init__(
        self,
        session: Session,
        job_repo: JobRepository,
        document_parsing_service: DocumentParsingStep,
        expense_extraction_service: ExpenseExtractionStep,
        policy_retrieval_service: PolicyRetrievalStep,
        policy_evaluation_service: PolicyEvaluationStep,
        risk_service: RiskCheckStep,
        approval_workflow_service: ApprovalWorkflowStep,
    ) -> None:
        self.session = session
        self.job_repo = job_repo
        self.document_parsing_service = document_parsing_service
        self.expense_extraction_service = expense_extraction_service
        self.policy_retrieval_service = policy_retrieval_service
        self.policy_evaluation_service = policy_evaluation_service
        self.risk_service = risk_service
        self.approval_workflow_service = approval_workflow_service

    def run_job(self, job_id: int) -> dict:
        job = self.job_repo.get_by_id(job_id)
        if job is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

        self._update_job_status(job_id, JOB_STATUS_RUNNING)
        logger.info("Job orchestration start job_id=%s document_id=%s", job.id, job.document_id)

        try:
            self.document_parsing_service.parse_document(job.document_id)
            extraction_result = self.expense_extraction_service.extract_expense(job.document_id)
            expense_id = extraction_result["expense_id"]

            retrieval_result = self.policy_retrieval_service.retrieve_policy_context(expense_id)
            policy_chunks = retrieval_result["policy_chunks"]

            self.policy_evaluation_service.evaluate(
                expense_id=expense_id,
                policy_chunks=policy_chunks,
            )
            self.risk_service.check_risk(expense_id=expense_id)
            self.approval_workflow_service.decide(expense_id=expense_id)
        except Exception:
            self.session.rollback()
            self._mark_job_failed(job_id)
            logger.exception("Job orchestration failed job_id=%s", job_id)
            raise

        self._update_job_status(job_id, JOB_STATUS_COMPLETED)
        logger.info("Job orchestration success job_id=%s", job_id)
        return {
            "job_id": job_id,
            "status": JOB_STATUS_COMPLETED,
        }

    def _mark_job_failed(self, job_id: int) -> None:
        try:
            self._update_job_status(job_id, JOB_STATUS_FAILED)
        except Exception:
            self.session.rollback()
            logger.exception("Job orchestration failed status update job_id=%s", job_id)

    def _update_job_status(self, job_id: int, job_status: str) -> None:
        job = self.job_repo.update_status(job_id, job_status)
        if job is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        self.session.commit()
