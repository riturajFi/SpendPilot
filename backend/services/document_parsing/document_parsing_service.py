from logging import getLogger

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.repositories import DocumentRepository
from backend.services.document_parsing.parsers import DocumentParserFactory
from backend.services.expense_ingestion.storage import ParsedArtifactStore, RawArtifactStore

logger = getLogger(__name__)


class DocumentParsingService:
    def __init__(
        self,
        session: Session,
        document_repo: DocumentRepository,
        raw_store: RawArtifactStore,
        parsed_store: ParsedArtifactStore,
        parser_factory: DocumentParserFactory,
    ) -> None:
        self.session = session
        self.document_repo = document_repo
        self.raw_store = raw_store
        self.parsed_store = parsed_store
        self.parser_factory = parser_factory

    def parse_document(self, document_id: int) -> dict:
        document = self.document_repo.get_by_id(document_id)
        if document is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        try:
            logger.info("Document parse start document_id=%s", document_id)
            file_bytes = self.raw_store.read_file(document.file_key)
            parser = self.parser_factory.get_parser(document.file_type)
            parsed_text = parser.parse(file_bytes)
            parsed_key = self.parsed_store.save_text(document_id, parsed_text)
            self.document_repo.update_status(document_id, "parsed")
            self.session.commit()
            logger.info(
                "Document parse success document_id=%s parsed_key=%s",
                document_id,
                parsed_key,
            )
            return {"document_id": document_id, "parsed_key": parsed_key}
        except Exception:
            self.session.rollback()
            self.document_repo.update_status(document_id, "failed")
            self.session.commit()
            logger.exception("Document parse failed document_id=%s", document_id)
            raise
