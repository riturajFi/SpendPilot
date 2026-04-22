from logging import getLogger

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.repositories import PolicyRepository
from backend.services.policy_indexing.contracts import PolicyDocument
from backend.services.policy_indexing import PolicyIndexingService
from backend.services.policy_management.commands import (
    CreatePolicyCommand,
    DeletePolicyCommand,
    UpdatePolicyCommand,
)
from backend.services.policy_management.policy_mapper import (
    to_policy_document,
    to_policy_response,
)

logger = getLogger(__name__)


class PolicyCommandService:
    def __init__(
        self,
        session: Session,
        policy_repository: PolicyRepository,
        policy_indexing_service: PolicyIndexingService,
    ) -> None:
        self.session = session
        self.policy_repository = policy_repository
        self.policy_indexing_service = policy_indexing_service

    def create_policy(self, command: CreatePolicyCommand) -> dict:
        policy = self.policy_repository.create(title=command.title, content=command.content)
        document = to_policy_document(policy)

        try:
            logger.info("Policy create start policy_id=%s", policy.id)
            self.policy_indexing_service.index_policy(document)
            self.session.commit()
            logger.info("Policy create success policy_id=%s", policy.id)
        except Exception:
            self.session.rollback()
            logger.exception("Policy create failed policy_id=%s", policy.id)
            self._cleanup_index(policy.id)
            raise

        return to_policy_response(policy)

    def update_policy(self, command: UpdatePolicyCommand) -> dict:
        policy = self.policy_repository.get_by_id(command.policy_id)
        if policy is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")

        original_document = to_policy_document(policy)
        policy.title = command.title
        policy.content = command.content
        updated_document = to_policy_document(policy)

        try:
            logger.info("Policy update start policy_id=%s", policy.id)
            self.policy_indexing_service.reindex_policy(updated_document)
            self.session.commit()
            logger.info("Policy update success policy_id=%s", policy.id)
        except Exception:
            self.session.rollback()
            logger.exception("Policy update failed policy_id=%s", policy.id)
            self._restore_index(original_document)
            raise

        return to_policy_response(policy)

    def delete_policy(self, command: DeletePolicyCommand) -> None:
        policy = self.policy_repository.get_by_id(command.policy_id)
        if policy is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")

        document = to_policy_document(policy)

        try:
            logger.info("Policy delete start policy_id=%s", policy.id)
            self.policy_indexing_service.delete_policy_index(policy.id)
            self.policy_repository.delete(policy)
            self.session.commit()
            logger.info("Policy delete success policy_id=%s", policy.id)
        except Exception:
            self.session.rollback()
            logger.exception("Policy delete failed policy_id=%s", policy.id)
            self._restore_index(document)
            raise

    def _cleanup_index(self, policy_id: int) -> None:
        try:
            self.policy_indexing_service.delete_policy_index(policy_id)
        except Exception:
            logger.exception("Policy index cleanup failed policy_id=%s", policy_id)

    def _restore_index(self, document: PolicyDocument) -> None:
        try:
            self.policy_indexing_service.reindex_policy(document)
        except Exception:
            logger.exception("Policy index restore failed policy_id=%s", document.policy_id)
