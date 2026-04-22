from sqlalchemy.orm import Session

from backend.models import Job


class JobRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, job_id: int) -> Job | None:
        return self.session.get(Job, job_id)

    def create(self, document_id: int, status: str) -> Job:
        job = Job(document_id=document_id, status=status)
        self.session.add(job)
        self.session.flush()
        return job

    def update_status(self, job_id: int, status: str) -> Job | None:
        job = self.get_by_id(job_id)
        if job is None:
            return None

        job.status = status
        self.session.flush()
        return job
