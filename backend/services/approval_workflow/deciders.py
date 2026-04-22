from abc import ABC, abstractmethod

from backend.services.expense_pipeline_statuses import (
    EXPENSE_STATUS_APPROVED,
    EXPENSE_STATUS_FLAGGED,
    EXPENSE_STATUS_REJECTED,
)


class ApprovalDecider(ABC):
    @abstractmethod
    def decide(self, policy_result: str, risk_signals: list) -> str:
        raise NotImplementedError


class SimpleApprovalDecider(ApprovalDecider):
    def decide(self, policy_result: str, risk_signals: list) -> str:
        normalized_policy_result = policy_result.lower()

        if normalized_policy_result == "fail":
            return EXPENSE_STATUS_REJECTED
        if normalized_policy_result == "warn":
            return EXPENSE_STATUS_FLAGGED
        if risk_signals:
            return EXPENSE_STATUS_FLAGGED
        if normalized_policy_result == "pass":
            return EXPENSE_STATUS_APPROVED
        raise ValueError(f"Unsupported policy result: {policy_result}")
