from abc import ABC, abstractmethod
from dataclasses import dataclass

from backend.services.openai_json import OpenAIJSONClient


@dataclass(frozen=True)
class ExtractedExpense:
    merchant: str
    amount: float | None
    currency: str
    expense_date: str
    category: str


class ExpenseExtractor(ABC):
    @abstractmethod
    def extract(self, text: str) -> ExtractedExpense:
        raise NotImplementedError


class OpenAIExpenseExtractor(ExpenseExtractor):
    SYSTEM_PROMPT = """
Extract structured expense data from parsed expense text.
Return JSON only with keys:
- merchant: string
- amount: number
- currency: string
- expense_date: string in YYYY-MM-DD when possible
- category: string
Use best effort. Do not include extra keys.
""".strip()

    def __init__(self, client: OpenAIJSONClient) -> None:
        self.client = client

    def extract(self, text: str) -> ExtractedExpense:
        payload = self.client.generate_json(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=f"Parsed expense text:\n{text}",
        )
        return ExtractedExpense(
            merchant=str(payload.get("merchant", "")).strip(),
            amount=float(payload.get("amount")) if payload.get("amount") is not None else None,
            currency=str(payload.get("currency", "")).strip().upper(),
            expense_date=str(payload.get("expense_date", "")).strip(),
            category=str(payload.get("category", "")).strip().lower(),
        )
