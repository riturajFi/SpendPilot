from backend.services.policy_indexing import PolicyIndexingService
from backend.services.policy_retrieval.retrievers import EmbeddingPolicyRetriever


def build_policy_retriever(policy_indexing_service: PolicyIndexingService) -> EmbeddingPolicyRetriever:
    return EmbeddingPolicyRetriever(
        embedding_provider=policy_indexing_service.embedding_provider,
        vector_store=policy_indexing_service.vector_store,
    )
