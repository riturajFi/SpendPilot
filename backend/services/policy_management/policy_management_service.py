from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.models import Policy
from backend.repositories import PolicyRepository
from backend.services.policy_management.commands import (
    CreatePolicyCommand,
    DeletePolicyCommand,
    UpdatePolicyCommand,
)


class PolicyManagementService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.policy_repository = PolicyRepository(session)

    def create_policy(self, command: CreatePolicyCommand) -> dict[str, int]:
        policy = self.policy_repository.create(title=command.title, content=command.content)
        self.session.commit()
        return {"policy_id": policy.id}

    def update_policy(self, command: UpdatePolicyCommand) -> dict[str, int]:
        policy = self.policy_repository.get_by_id(command.policy_id)
        if policy is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")

        policy.title = command.title
        policy.content = command.content
        self.session.commit()
        return {"policy_id": policy.id}

    def get_policy(self, policy_id: int) -> dict:
        policy = self.policy_repository.get_by_id(policy_id)
        if policy is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
        return self._serialize_policy(policy)

    def get_policies(self) -> list[dict]:
        return [self._serialize_policy(policy) for policy in self.policy_repository.list_all()]

    def delete_policy(self, command: DeletePolicyCommand) -> None:
        policy = self.policy_repository.get_by_id(command.policy_id)
        if policy is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
        self.policy_repository.delete(policy)
        self.session.commit()

    @staticmethod
    def _serialize_policy(policy: Policy) -> dict:
        return {
            "id": policy.id,
            "title": policy.title,
            "content": policy.content,
            "created_at": policy.created_at,
        }
