from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.repositories import ExpenseRepository, PolicyResultRepository, RiskSignalRepository
from backend.services.approval_workflow.deciders import ApprovalDecider


class ApprovalWorkflowService:
    def __init__(
        self,
        session: Session,
        expense_repo: ExpenseRepository,
        policy_result_repo: PolicyResultRepository,
        risk_signal_repo: RiskSignalRepository,
        decider: ApprovalDecider,
    ) -> None:
        self.session = session
        self.expense_repo = expense_repo
        self.policy_result_repo = policy_result_repo
        self.risk_signal_repo = risk_signal_repo
        self.decider = decider

    def decide(self, expense_id: int) -> dict:
        expense = self.expense_repo.get_by_id(expense_id)
        if expense is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")

        policy_result = self.policy_result_repo.get_by_expense_id(expense_id)
        if policy_result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Policy result not found",
            )

        risk_signals = self.risk_signal_repo.list_by_expense_id(expense_id)
        final_status = self.decider.decide(
            policy_result=policy_result.result,
            risk_signals=risk_signals,
        )
        self.expense_repo.update_status(expense.id, final_status)
        self.session.commit()
        return {
            "expense_id": expense.id,
            "status": final_status,
        }
