from backend.models import Expense, PolicyResult, RiskSignal


def to_expense_list_item(expense: Expense) -> dict:
    return {
        "id": expense.id,
        "merchant": expense.merchant,
        "amount": expense.amount,
        "currency": expense.currency,
        "category": expense.category,
        "status": expense.status,
        "expense_date": expense.expense_date,
    }


def to_expense_detail_view(
    expense: Expense,
    policy_result: PolicyResult | None,
    risk_signals: list[RiskSignal],
) -> dict:
    return {
        "id": expense.id,
        "merchant": expense.merchant,
        "amount": expense.amount,
        "currency": expense.currency,
        "expense_date": expense.expense_date,
        "category": expense.category,
        "status": expense.status,
        "policy_result": policy_result.result if policy_result else None,
        "policy_reason": policy_result.reason if policy_result else None,
        "risk_signals": [risk_signal.signal_type for risk_signal in risk_signals],
    }
