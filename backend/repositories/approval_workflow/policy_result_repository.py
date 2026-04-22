from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import PolicyResult


class PolicyResultRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_expense_id(self, expense_id: int) -> PolicyResult | None:
        stmt = select(PolicyResult).where(PolicyResult.expense_id == expense_id)
        return self.session.scalar(stmt)
