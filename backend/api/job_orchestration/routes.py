from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from backend.api.job_orchestration.schemas import JobRunResponse
from backend.dependencies import get_db_session
from backend.repositories import (
    DocumentRepository,
    ExpenseRepository,
    JobRepository,
    PolicyResultRepository,
    RiskSignalRepository,
)
from backend.services.approval_workflow import ApprovalWorkflowService, SimpleApprovalDecider
from backend.services.document_parsing import DocumentParsingService, SimpleDocumentParserFactory
from backend.services.expense_extraction import ExpenseExtractionService, ExpenseExtractor
from backend.services.expense_ingestion import LocalParsedArtifactStore, LocalRawArtifactStore
from backend.services.job_orchestration import JobOrchestrationService
from backend.services.policy_evaluation import PolicyEvaluationService, PolicyEvaluator
from backend.services.policy_retrieval import PolicyRetriever, PolicyRetrievalService
from backend.services.risk_check import RiskService


router = APIRouter(prefix="/jobs", tags=["job-orchestration"])


def get_job_orchestration_service(
    request: Request,
    session: Session = Depends(get_db_session),
) -> JobOrchestrationService:
    document_repo = DocumentRepository(session)
    expense_repo = ExpenseRepository(session)
    policy_result_repo = PolicyResultRepository(session)
    risk_signal_repo = RiskSignalRepository(session)

    expense_extractor: ExpenseExtractor = request.app.state.expense_extractor
    policy_retriever: PolicyRetriever = request.app.state.policy_retriever
    policy_evaluator: PolicyEvaluator = request.app.state.policy_evaluator

    return JobOrchestrationService(
        session=session,
        job_repo=JobRepository(session),
        document_parsing_service=DocumentParsingService(
            session=session,
            document_repo=document_repo,
            raw_store=LocalRawArtifactStore(),
            parsed_store=LocalParsedArtifactStore(),
            parser_factory=SimpleDocumentParserFactory(),
        ),
        expense_extraction_service=ExpenseExtractionService(
            session=session,
            document_repo=document_repo,
            parsed_store=LocalParsedArtifactStore(),
            expense_repo=expense_repo,
            extractor=expense_extractor,
        ),
        policy_retrieval_service=PolicyRetrievalService(
            expense_repo=expense_repo,
            retriever=policy_retriever,
        ),
        policy_evaluation_service=PolicyEvaluationService(
            session=session,
            expense_repo=expense_repo,
            policy_result_repo=policy_result_repo,
            evaluator=policy_evaluator,
        ),
        risk_service=RiskService(
            session=session,
            expense_repo=expense_repo,
            risk_signal_repo=risk_signal_repo,
        ),
        approval_workflow_service=ApprovalWorkflowService(
            session=session,
            expense_repo=expense_repo,
            policy_result_repo=policy_result_repo,
            risk_signal_repo=risk_signal_repo,
            decider=SimpleApprovalDecider(),
        ),
    )


@router.post("/{job_id}/run", response_model=JobRunResponse, status_code=status.HTTP_200_OK)
def run_job(
    job_id: int,
    service: JobOrchestrationService = Depends(get_job_orchestration_service),
) -> JobRunResponse:
    return JobRunResponse(**service.run_job(job_id))
