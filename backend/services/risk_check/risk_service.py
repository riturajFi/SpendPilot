from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.repositories import ExpenseRepository, RiskSignalRepository


class RiskService:
    HIGH_AMOUNT_THRESHOLD = 1000.0
    HIGH_RISK_CATEGORIES = {"alcohol", "gift", "gift_card", "entertainment"}
    CASH_LIKE_MERCHANT_MARKERS = {"atm", "cash", "withdrawal"}

    def __init__(
        self,
        session: Session,
        expense_repo: ExpenseRepository,
        risk_signal_repo: RiskSignalRepository,
    ) -> None:
        self.session = session
        self.expense_repo = expense_repo
        self.risk_signal_repo = risk_signal_repo

    def check_risk(self, expense_id: int) -> dict:
        expense = self.expense_repo.get_by_id(expense_id)
        if expense is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")

        signal_types = self._build_signal_types(expense)
        signals = self.risk_signal_repo.replace_for_expense(expense_id=expense.id, signal_types=signal_types)
        self.session.commit()
        return {
            "expense_id": expense.id,
            "risk_signals": [signal.signal_type for signal in signals],
        }

    def _build_signal_types(self, expense) -> list[str]:
        signal_types: list[str] = []

        if expense.amount >= self.HIGH_AMOUNT_THRESHOLD:
            signal_types.append("large_amount")
        if expense.category.lower() in self.HIGH_RISK_CATEGORIES:
            signal_types.append("high_risk_category")
        if any(marker in expense.merchant.lower() for marker in self.CASH_LIKE_MERCHANT_MARKERS):
            signal_types.append("cash_like_merchant")
        if self._is_weekend(expense.expense_date):
            signal_types.append("weekend_expense")

        return signal_types

    def _is_weekend(self, expense_date: str) -> bool:
        try:
            parsed_date = datetime.strptime(expense_date, "%Y-%m-%d")
        except ValueError:
            return False
        return parsed_date.weekday() >= 5
