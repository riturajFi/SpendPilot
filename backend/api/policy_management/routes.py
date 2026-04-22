from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.api.policy_management.schemas import (
    CreatePolicyRequest,
    CreatePolicyResponse,
    PolicyResponse,
    UpdatePolicyRequest,
)
from backend.dependencies import get_db_session
from backend.services.policy_management import PolicyManagementService
from backend.services.policy_management.commands import (
    CreatePolicyCommand,
    DeletePolicyCommand,
    UpdatePolicyCommand,
)


router = APIRouter(prefix="/policies", tags=["policy-management"])


def get_policy_management_service(
    session: Session = Depends(get_db_session),
) -> PolicyManagementService:
    return PolicyManagementService(session)


@router.post("", response_model=CreatePolicyResponse, status_code=status.HTTP_201_CREATED)
def create_policy(
    request: CreatePolicyRequest,
    service: PolicyManagementService = Depends(get_policy_management_service),
) -> CreatePolicyResponse:
    return CreatePolicyResponse(
        **service.create_policy(CreatePolicyCommand(title=request.title, content=request.content))
    )


@router.put("/{policy_id}", response_model=PolicyResponse)
def update_policy(
    policy_id: int,
    request: UpdatePolicyRequest,
    service: PolicyManagementService = Depends(get_policy_management_service),
) -> PolicyResponse:
    updated = service.update_policy(
        UpdatePolicyCommand(
            policy_id=policy_id,
            title=request.title,
            content=request.content,
        )
    )
    return PolicyResponse(**service.get_policy(updated["policy_id"]))


@router.get("", response_model=list[PolicyResponse])
def get_policies(
    service: PolicyManagementService = Depends(get_policy_management_service),
) -> list[PolicyResponse]:
    return [PolicyResponse(**item) for item in service.get_policies()]


@router.get("/{policy_id}", response_model=PolicyResponse)
def get_policy(
    policy_id: int,
    service: PolicyManagementService = Depends(get_policy_management_service),
) -> PolicyResponse:
    return PolicyResponse(**service.get_policy(policy_id))


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_policy(
    policy_id: int,
    service: PolicyManagementService = Depends(get_policy_management_service),
) -> None:
    service.delete_policy(DeletePolicyCommand(policy_id=policy_id))
