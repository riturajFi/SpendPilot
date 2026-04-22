from sqlalchemy.orm import Session

from backend.models import Expense


class ExpenseRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

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
