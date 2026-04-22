from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import RiskSignal


class RiskSignalRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_by_expense_id(self, expense_id: int) -> list[RiskSignal]:
        stmt = select(RiskSignal).where(RiskSignal.expense_id == expense_id)
        return list(self.session.scalars(stmt))
