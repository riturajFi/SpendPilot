import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.expense_ingestion.routes import router as expense_router
from backend.api.expense_query.routes import router as expense_query_router
from backend.api.policy_management.routes import router as policy_router
from backend.db import initialize_database
from backend.services.policy_indexing.bootstrap import build_policy_indexing_service


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    app.state.policy_indexing_service = build_policy_indexing_service()
    yield


app = FastAPI(title="SpendPilot Backend", lifespan=lifespan)
app.include_router(expense_router)
app.include_router(expense_query_router)
app.include_router(policy_router)
