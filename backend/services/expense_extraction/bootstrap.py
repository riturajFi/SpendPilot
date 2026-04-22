import os
from dataclasses import dataclass

from backend.services.expense_extraction.extractors import OpenAIExpenseExtractor
from backend.services.openai_json import OpenAIJSONClient


@dataclass(frozen=True)
class ExpenseExtractionSettings:
    openai_api_key: str | None
    model: str

    @classmethod
    def from_env(cls) -> "ExpenseExtractionSettings":
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("OPENAI_EXPENSE_EXTRACTION_MODEL", "gpt-4o-mini"),
        )


def build_expense_extractor() -> OpenAIExpenseExtractor:
    settings = ExpenseExtractionSettings.from_env()
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required for expense extraction")
    client = OpenAIJSONClient(api_key=settings.openai_api_key, model=settings.model)
    return OpenAIExpenseExtractor(client=client)
