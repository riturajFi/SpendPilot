from sqlalchemy.orm import Session

from backend.models import Job


class JobRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, document_id: int, status: str) -> Job:
        job = Job(document_id=document_id, status=status)
        self.session.add(job)
        self.session.flush()
        return job
