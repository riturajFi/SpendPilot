from backend.models import Policy
from backend.services.policy_indexing.contracts import PolicyDocument


def to_policy_document(policy: Policy) -> PolicyDocument:
    return PolicyDocument(
        policy_id=policy.id,
        title=policy.title,
        content=policy.content,
    )


def to_policy_response(policy: Policy) -> dict:
    return {
        "id": policy.id,
        "title": policy.title,
        "content": policy.content,
        "created_at": policy.created_at,
    }

