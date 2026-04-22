from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import PolicyResult


class PolicyResultRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_expense_id(self, expense_id: int) -> PolicyResult | None:
        stmt = select(PolicyResult).where(PolicyResult.expense_id == expense_id)
        return self.session.scalar(stmt)

    def upsert(self, expense_id: int, result: str, reason: str) -> PolicyResult:
        policy_result = self.get_by_expense_id(expense_id)
        if policy_result is None:
            policy_result = PolicyResult(expense_id=expense_id, result=result, reason=reason)
            self.session.add(policy_result)
        else:
            policy_result.result = result
            policy_result.reason = reason
        self.session.flush()
        return policy_result
