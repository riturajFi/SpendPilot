from fastapi import HTTPException, status

from backend.models import Expense
from backend.repositories import ExpenseRepository
from backend.services.policy_retrieval.retrievers import PolicyChunk, PolicyRetriever


class PolicyRetrievalService:
    DEFAULT_TOP_K = 5

    def __init__(
        self,
        expense_repo: ExpenseRepository,
        retriever: PolicyRetriever,
    ) -> None:
        self.expense_repo = expense_repo
        self.retriever = retriever

    def retrieve_policy_context(self, expense_id: int) -> dict:
        expense = self.expense_repo.get_by_id(expense_id)
        if expense is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")

        query = self._build_query(expense)
        chunks = self.retriever.retrieve(query=query, top_k=self.DEFAULT_TOP_K)
        return {
            "expense_id": expense.id,
            "policy_chunks": [self._to_chunk_payload(chunk) for chunk in chunks],
        }

    def _build_query(self, expense: Expense) -> str:
        return (
            f"category: {expense.category}, "
            f"merchant: {expense.merchant}, "
            f"amount: {expense.amount} {expense.currency}"
        )

    def _to_chunk_payload(self, chunk: PolicyChunk) -> dict:
        return {
            "chunk_id": chunk.chunk_id,
            "text": chunk.text,
        }
