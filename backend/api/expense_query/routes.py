from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.api.expense_query.schemas import (
    ExpenseDetailView,
    ExpenseListItem,
    ExpenseSummaryView,
)
from backend.dependencies import get_db_session
from backend.repositories import (
    ExpenseRepository,
    ExpenseSummaryRepository,
    PolicyResultRepository,
    RiskSignalRepository,
)
from backend.services.expense_query import ExpenseQueryService


router = APIRouter(prefix="/expenses", tags=["expense-query"])


def get_expense_query_service(
    session: Session = Depends(get_db_session),
) -> ExpenseQueryService:
    return ExpenseQueryService(
        expense_repo=ExpenseRepository(session),
        policy_result_repo=PolicyResultRepository(session),
        risk_signal_repo=RiskSignalRepository(session),
        summary_repo=ExpenseSummaryRepository(session),
    )


@router.get("", response_model=list[ExpenseListItem])
def list_expenses(
    status: str | None = None,
    category: str | None = None,
    expense_date: str | None = None,
    service: ExpenseQueryService = Depends(get_expense_query_service),
) -> list[ExpenseListItem]:
    return [
        ExpenseListItem(**item)
        for item in service.list_expenses(
            status=status,
            category=category,
            expense_date=expense_date,
        )
    ]


@router.get("/summary", response_model=ExpenseSummaryView)
def get_summary(
    status: str | None = None,
    category: str | None = None,
    expense_date: str | None = None,
    service: ExpenseQueryService = Depends(get_expense_query_service),
) -> ExpenseSummaryView:
    return ExpenseSummaryView(
        **service.get_summary(
            status=status,
            category=category,
            expense_date=expense_date,
        )
    )


@router.get("/{expense_id}", response_model=ExpenseDetailView)
def get_expense_detail(
    expense_id: int,
    service: ExpenseQueryService = Depends(get_expense_query_service),
) -> ExpenseDetailView:
    return ExpenseDetailView(**service.get_expense_detail(expense_id))
