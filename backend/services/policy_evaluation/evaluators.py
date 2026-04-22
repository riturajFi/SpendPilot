from abc import ABC, abstractmethod
from dataclasses import dataclass

from backend.models import Expense
from backend.services.openai_json import OpenAIJSONClient


@dataclass(frozen=True)
class PolicyDecision:
    result: str
    reason: str


class PolicyEvaluator(ABC):
    @abstractmethod
    def evaluate(self, expense: Expense, policy_chunks: list[dict]) -> PolicyDecision:
        raise NotImplementedError


class OpenAIPolicyEvaluator(PolicyEvaluator):
    SYSTEM_PROMPT = """
Evaluate whether expense complies with provided policy context.
Return JSON only with keys:
- result: one of pass, warn, fail
- reason: short explanation
Use only provided expense data and policy chunks.
Choose:
- fail when policy clearly disallows expense
- warn when policy coverage is partial or ambiguous
- pass when policy clearly allows expense
""".strip()

    def __init__(self, client: OpenAIJSONClient) -> None:
        self.client = client

    def evaluate(self, expense: Expense, policy_chunks: list[dict]) -> PolicyDecision:
        chunks_text = "\n".join(
            f"- {chunk['chunk_id']}: {chunk['text']}" for chunk in policy_chunks
        )
        user_prompt = f"""
Expense:
- merchant: {expense.merchant}
- amount: {expense.amount}
- currency: {expense.currency}
- expense_date: {expense.expense_date}
- category: {expense.category}

Policy chunks:
{chunks_text}
""".strip()
        payload = self.client.generate_json(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )
        return PolicyDecision(
            result=str(payload.get("result", "")).strip().lower(),
            reason=str(payload.get("reason", "")).strip(),
        )
