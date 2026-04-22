from abc import ABC, abstractmethod


class DocumentParsingStep(ABC):
    @abstractmethod
    def parse_document(self, document_id: int) -> dict:
        raise NotImplementedError


class ExpenseExtractionStep(ABC):
    @abstractmethod
    def extract_expense(self, document_id: int) -> dict:
        raise NotImplementedError


class PolicyRetrievalStep(ABC):
    @abstractmethod
    def retrieve_policy_context(self, expense_id: int) -> dict:
        raise NotImplementedError


class PolicyEvaluationStep(ABC):
    @abstractmethod
    def evaluate(self, expense_id: int, policy_chunks: list[dict]) -> dict:
        raise NotImplementedError


class RiskCheckStep(ABC):
    @abstractmethod
    def check_risk(self, expense_id: int) -> dict:
        raise NotImplementedError


class ApprovalWorkflowStep(ABC):
    @abstractmethod
    def decide(self, expense_id: int) -> dict:
        raise NotImplementedError
