from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ExtractedExpense:
    merchant: str
    amount: float
    currency: str
    expense_date: str
    category: str


class ExpenseExtractor(ABC):
    @abstractmethod
    def extract(self, text: str) -> ExtractedExpense:
        raise NotImplementedError
