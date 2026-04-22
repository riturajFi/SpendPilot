from sqlalchemy.orm import Session

from backend.models import Document


class DocumentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, file_key: str, file_type: str, status: str) -> Document:
        document = Document(file_key=file_key, file_type=file_type, status=status)
        self.session.add(document)
        self.session.flush()
        return document

    def get_by_id(self, document_id: int) -> Document | None:
        return self.session.get(Document, document_id)

    def update_status(self, document_id: int, status: str) -> Document | None:
        document = self.get_by_id(document_id)
        if document is None:
            return None

        document.status = status
        self.session.flush()
        return document
