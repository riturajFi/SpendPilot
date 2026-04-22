from sqlalchemy import Select, case, func, select
from sqlalchemy.orm import Session

from backend.models import Expense
from backend.services.expense_pipeline_statuses import (
    EXPENSE_STATUS_APPROVED,
    EXPENSE_STATUS_FLAGGED,
    EXPENSE_STATUS_REJECTED,
)


class ExpenseSummaryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_summary(
        self,
        status: str | None = None,
        category: str | None = None,
        expense_date: str | None = None,
    ) -> dict:
        stmt = select(
            func.count(Expense.id).label("total_expenses"),
            func.coalesce(
                func.sum(case((Expense.status == EXPENSE_STATUS_APPROVED, 1), else_=0)),
                0,
            ).label("approved_count"),
            func.coalesce(
                func.sum(case((Expense.status == EXPENSE_STATUS_FLAGGED, 1), else_=0)),
                0,
            ).label("flagged_count"),
            func.coalesce(
                func.sum(case((Expense.status == EXPENSE_STATUS_REJECTED, 1), else_=0)),
                0,
            ).label("rejected_count"),
            func.coalesce(func.sum(Expense.amount), 0.0).label("total_amount"),
        )
        filtered_stmt = self._apply_filters(
            stmt=stmt,
            status=status,
            category=category,
            expense_date=expense_date,
        )
        row = self.session.execute(filtered_stmt).one()
        return {
            "total_expenses": row.total_expenses,
            "approved_count": row.approved_count,
            "flagged_count": row.flagged_count,
            "rejected_count": row.rejected_count,
            "total_amount": float(row.total_amount),
        }

    def _apply_filters(
        self,
        stmt: Select,
        status: str | None,
        category: str | None,
        expense_date: str | None,
    ) -> Select:
        if status:
            stmt = stmt.where(Expense.status == status)
        if category:
            stmt = stmt.where(Expense.category == category)
        if expense_date:
            stmt = stmt.where(Expense.expense_date == expense_date)
        return stmt
