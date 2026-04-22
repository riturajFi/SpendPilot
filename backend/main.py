import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.expense_ingestion.routes import router as expense_router
from backend.api.expense_query.routes import router as expense_query_router
from backend.api.job_orchestration.routes import router as job_orchestration_router
from backend.api.policy_management.routes import router as policy_router
from backend.db import initialize_database
from backend.services.expense_extraction import build_expense_extractor
from backend.services.policy_evaluation import build_policy_evaluator
from backend.services.policy_indexing.bootstrap import build_policy_indexing_service
from backend.services.policy_retrieval import build_policy_retriever


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    app.state.policy_indexing_service = build_policy_indexing_service()
    app.state.expense_extractor = build_expense_extractor()
    app.state.policy_retriever = build_policy_retriever(app.state.policy_indexing_service)
    app.state.policy_evaluator = build_policy_evaluator()
    yield


app = FastAPI(title="SpendPilot Backend", lifespan=lifespan)
app.include_router(expense_router)
app.include_router(expense_query_router)
app.include_router(job_orchestration_router)
app.include_router(policy_router)
