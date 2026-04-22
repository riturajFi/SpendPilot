from pydantic import BaseModel


class ExpenseListItem(BaseModel):
    id: int
    merchant: str
    amount: float
    currency: str
    category: str
    status: str
    expense_date: str


class ExpenseDetailView(BaseModel):
    id: int
    merchant: str
    amount: float
    currency: str
    expense_date: str
    category: str
    status: str
    policy_result: str | None
    policy_reason: str | None
    risk_signals: list[str]


class ExpenseSummaryView(BaseModel):
    total_expenses: int
    approved_count: int
    flagged_count: int
    rejected_count: int
    total_amount: float
