from backend.repositories import PolicyRepository
from backend.services.policy_management.policy_mapper import to_policy_response


class PolicyQueryService:
    def __init__(self, policy_repository: PolicyRepository) -> None:
        self.policy_repository = policy_repository

    def get_policy(self, policy_id: int) -> dict | None:
        policy = self.policy_repository.get_by_id(policy_id)
        if policy is None:
            return None
        return to_policy_response(policy)

    def get_policies(self) -> list[dict]:
        return [to_policy_response(policy) for policy in self.policy_repository.list_all()]

