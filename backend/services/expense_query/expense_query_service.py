from fastapi import HTTPException, status

from backend.repositories import (
    ExpenseRepository,
    ExpenseSummaryRepository,
    PolicyResultRepository,
    RiskSignalRepository,
)
from backend.services.expense_query.expense_query_mapper import (
    to_expense_detail_view,
    to_expense_list_item,
)


class ExpenseQueryService:
    def __init__(
        self,
        expense_repo: ExpenseRepository,
        policy_result_repo: PolicyResultRepository,
        risk_signal_repo: RiskSignalRepository,
        summary_repo: ExpenseSummaryRepository,
    ) -> None:
        self.expense_repo = expense_repo
        self.policy_result_repo = policy_result_repo
        self.risk_signal_repo = risk_signal_repo
        self.summary_repo = summary_repo

    def list_expenses(
        self,
        status: str | None = None,
        category: str | None = None,
        expense_date: str | None = None,
    ) -> list[dict]:
        expenses = self.expense_repo.list(
            status=status,
            category=category,
            expense_date=expense_date,
        )
        return [to_expense_list_item(expense) for expense in expenses]

    def get_expense_detail(self, expense_id: int) -> dict:
        expense = self.expense_repo.get_by_id(expense_id)
        if expense is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")

        policy_result = self.policy_result_repo.get_by_expense_id(expense_id)
        risk_signals = self.risk_signal_repo.list_by_expense_id(expense_id)
        return to_expense_detail_view(
            expense=expense,
            policy_result=policy_result,
            risk_signals=risk_signals,
        )

    def get_summary(
        self,
        status: str | None = None,
        category: str | None = None,
        expense_date: str | None = None,
    ) -> dict:
        return self.summary_repo.get_summary(
            status=status,
            category=category,
            expense_date=expense_date,
        )
