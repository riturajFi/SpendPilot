from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import Policy


class PolicyRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, title: str, content: str) -> Policy:
        policy = Policy(title=title, content=content)
        self.session.add(policy)
        self.session.flush()
        return policy

    def get_by_id(self, policy_id: int) -> Policy | None:
        return self.session.get(Policy, policy_id)

    def list_all(self) -> list[Policy]:
        stmt = select(Policy).order_by(Policy.id.asc())
        return list(self.session.scalars(stmt))

    def delete(self, policy: Policy) -> None:
        self.session.delete(policy)
