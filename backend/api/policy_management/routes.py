from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.api.policy_management.schemas import (
    CreatePolicyRequest,
    PolicyResponse,
    UpdatePolicyRequest,
)
from backend.dependencies import get_db_session
from backend.repositories import PolicyRepository
from backend.services.policy_indexing import PolicyIndexingService
from backend.services.policy_management.commands import (
    CreatePolicyCommand,
    DeletePolicyCommand,
    UpdatePolicyCommand,
)
from backend.services.policy_management import PolicyCommandService, PolicyQueryService


router = APIRouter(prefix="/policies", tags=["policy-management"])


def get_policy_query_service(
    session: Session = Depends(get_db_session),
) -> PolicyQueryService:
    return PolicyQueryService(PolicyRepository(session))


def get_policy_command_service(
    request: Request,
    session: Session = Depends(get_db_session),
) -> PolicyCommandService:
    policy_repository = PolicyRepository(session)
    policy_indexing_service: PolicyIndexingService = request.app.state.policy_indexing_service
    return PolicyCommandService(
        session=session,
        policy_repository=policy_repository,
        policy_indexing_service=policy_indexing_service,
    )


@router.post("", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
def create_policy(
    request: CreatePolicyRequest,
    service: PolicyCommandService = Depends(get_policy_command_service),
) -> PolicyResponse:
    return PolicyResponse(
        **service.create_policy(CreatePolicyCommand(title=request.title, content=request.content))
    )


@router.put("/{policy_id}", response_model=PolicyResponse)
def update_policy(
    policy_id: int,
    request: UpdatePolicyRequest,
    service: PolicyCommandService = Depends(get_policy_command_service),
) -> PolicyResponse:
    return PolicyResponse(
        **service.update_policy(
            UpdatePolicyCommand(
                policy_id=policy_id,
                title=request.title,
                content=request.content,
            )
        )
    )


@router.get("", response_model=list[PolicyResponse])
def get_policies(
    service: PolicyQueryService = Depends(get_policy_query_service),
) -> list[PolicyResponse]:
    return [PolicyResponse(**item) for item in service.get_policies()]


@router.get("/{policy_id}", response_model=PolicyResponse)
def get_policy(
    policy_id: int,
    service: PolicyQueryService = Depends(get_policy_query_service),
) -> PolicyResponse:
    policy = service.get_policy(policy_id)
    if policy is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
    return PolicyResponse(**policy)


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_policy(
    policy_id: int,
    service: PolicyCommandService = Depends(get_policy_command_service),
) -> None:
    service.delete_policy(DeletePolicyCommand(policy_id=policy_id))
