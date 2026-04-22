from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.repositories import ExpenseRepository, PolicyResultRepository
from backend.services.policy_evaluation.evaluators import PolicyDecision, PolicyEvaluator


class PolicyEvaluationService:
    def __init__(
        self,
        session: Session,
        expense_repo: ExpenseRepository,
        policy_result_repo: PolicyResultRepository,
        evaluator: PolicyEvaluator,
    ) -> None:
        self.session = session
        self.expense_repo = expense_repo
        self.policy_result_repo = policy_result_repo
        self.evaluator = evaluator

    def evaluate(self, expense_id: int, policy_chunks: list[dict]) -> dict:
        expense = self.expense_repo.get_by_id(expense_id)
        if expense is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")

        decision = self.evaluator.evaluate(expense=expense, policy_chunks=policy_chunks)
        self._validate_decision(decision)
        policy_result = self.policy_result_repo.upsert(
            expense_id=expense.id,
            result=decision.result,
            reason=decision.reason,
        )
        self.session.commit()
        return {
            "expense_id": expense.id,
            "result": policy_result.result,
            "reason": policy_result.reason,
        }

    def _validate_decision(self, decision: PolicyDecision) -> None:
        if decision.result not in {"pass", "warn", "fail"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported policy evaluation result: {decision.result}",
            )
        if not decision.reason:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Policy evaluation reason is required",
            )
