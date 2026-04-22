from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import RiskSignal


class RiskSignalRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_by_expense_id(self, expense_id: int) -> list[RiskSignal]:
        stmt = select(RiskSignal).where(RiskSignal.expense_id == expense_id).order_by(RiskSignal.id.asc())
        return list(self.session.scalars(stmt))

    def replace_for_expense(self, expense_id: int, signal_types: list[str]) -> list[RiskSignal]:
        existing_signals = self.list_by_expense_id(expense_id)
        for signal in existing_signals:
            self.session.delete(signal)
        self.session.flush()

        signals: list[RiskSignal] = []
        for signal_type in signal_types:
            signal = RiskSignal(expense_id=expense_id, signal_type=signal_type)
            self.session.add(signal)
            signals.append(signal)

        self.session.flush()
        return signals
