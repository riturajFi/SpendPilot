from logging import getLogger

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.repositories import DocumentRepository, ExpenseRepository
from backend.services.expense_extraction.extractors import ExpenseExtractor, ExtractedExpense
from backend.services.expense_ingestion.storage import ParsedArtifactStore
from backend.services.expense_pipeline_statuses import EXPENSE_STATUS_EXTRACTED

logger = getLogger(__name__)


class ExpenseExtractionService:
    def __init__(
        self,
        session: Session,
        document_repo: DocumentRepository,
        parsed_store: ParsedArtifactStore,
        expense_repo: ExpenseRepository,
        extractor: ExpenseExtractor,
    ) -> None:
        self.session = session
        self.document_repo = document_repo
        self.parsed_store = parsed_store
        self.expense_repo = expense_repo
        self.extractor = extractor

    def extract_expense(self, document_id: int) -> dict:
        document = self.document_repo.get_by_id(document_id)
        if document is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        logger.info("Expense extraction start document_id=%s", document_id)
        parsed_text = self.parsed_store.read_text(document.id)
        extracted = self.extractor.extract(parsed_text)
        self._validate_extracted_expense(extracted)

        try:
            expense = self.expense_repo.create(
                document_id=document.id,
                merchant=extracted.merchant,
                amount=extracted.amount,
                currency=extracted.currency,
                expense_date=extracted.expense_date,
                category=extracted.category,
                status=EXPENSE_STATUS_EXTRACTED,
            )
            self.session.commit()
            logger.info(
                "Expense extraction success document_id=%s expense_id=%s",
                document_id,
                expense.id,
            )
        except Exception:
            self.session.rollback()
            logger.exception("Expense extraction failed document_id=%s", document_id)
            raise

        return {"expense_id": expense.id}

    def _validate_extracted_expense(self, extracted: ExtractedExpense) -> None:
        missing_fields: list[str] = []

        if not extracted.merchant.strip():
            missing_fields.append("merchant")
        if extracted.amount is None:
            missing_fields.append("amount")
        if not extracted.currency.strip():
            missing_fields.append("currency")
        if not extracted.expense_date.strip():
            missing_fields.append("expense_date")
        if not extracted.category.strip():
            missing_fields.append("category")

        if missing_fields:
            fields = ", ".join(missing_fields)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing extracted expense fields: {fields}",
            )
