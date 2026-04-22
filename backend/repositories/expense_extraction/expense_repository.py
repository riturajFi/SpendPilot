from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import Expense


class ExpenseRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, expense_id: int) -> Expense | None:
        return self.session.get(Expense, expense_id)

    def list(
        self,
        status: str | None = None,
        category: str | None = None,
        expense_date: str | None = None,
    ) -> list[Expense]:
        stmt = select(Expense).order_by(Expense.id.desc())
        if status:
            stmt = stmt.where(Expense.status == status)
        if category:
            stmt = stmt.where(Expense.category == category)
        if expense_date:
            stmt = stmt.where(Expense.expense_date == expense_date)
        return list(self.session.scalars(stmt))

    def update_status(self, expense_id: int, status: str) -> Expense | None:
        expense = self.get_by_id(expense_id)
        if expense is None:
            return None

        expense.status = status
        self.session.flush()
        return expense

    def create(
        self,
        document_id: int,
        merchant: str,
        amount: float,
        currency: str,
        expense_date: str,
        category: str,
        status: str,
    ) -> Expense:
        expense = Expense(
            document_id=document_id,
            merchant=merchant,
            amount=amount,
            currency=currency,
            expense_date=expense_date,
            category=category,
            status=status,
        )
        self.session.add(expense)
        self.session.flush()
        return expense
