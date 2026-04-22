import os
from dataclasses import dataclass
from logging import getLogger

from backend.services.policy_indexing.chunkers import FixedSizeChunker
from backend.services.policy_indexing.embedding_providers import (
    MockEmbeddingProvider,
    OpenAIEmbeddingProvider,
)
from backend.services.policy_indexing.policy_indexing_service import PolicyIndexingService
from backend.services.policy_indexing.vector_stores import (
    InMemoryPolicyStore,
    PineconePolicyStore,
    QdrantPolicyStore,
)

logger = getLogger(__name__)


@dataclass(frozen=True)
class PolicyIndexingSettings:
    embedding_provider: str
    vector_store: str
    openai_api_key: str | None
    openai_embedding_model: str
    openai_embedding_dimensions: int | None
    pinecone_api_key: str | None
    pinecone_index_host: str | None
    pinecone_index_name: str | None
    pinecone_namespace: str

    @classmethod
    def from_env(cls) -> "PolicyIndexingSettings":
        dimensions = os.getenv("OPENAI_EMBEDDING_DIMENSIONS")
        return cls(
            embedding_provider=os.getenv("POLICY_EMBEDDING_PROVIDER", "mock").lower(),
            vector_store=os.getenv("POLICY_VECTOR_STORE", "memory").lower(),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            openai_embedding_dimensions=int(dimensions) if dimensions else None,
            pinecone_api_key=os.getenv("PINECONE_API_KEY"),
            pinecone_index_host=os.getenv("PINECONE_INDEX_HOST"),
            pinecone_index_name=os.getenv("PINECONE_INDEX_NAME"),
            pinecone_namespace=os.getenv("PINECONE_NAMESPACE", "policy-index"),
        )


_memory_store = InMemoryPolicyStore()


def build_policy_indexing_service() -> PolicyIndexingService:
    settings = PolicyIndexingSettings.from_env()
    chunker = FixedSizeChunker()
    return PolicyIndexingService(
        chunker=chunker,
        embedding_provider=build_embedding_provider(settings),
        vector_store=build_vector_store(settings),
    )


def build_embedding_provider(settings: PolicyIndexingSettings):
    logger.info("Policy indexing embedding provider=%s", settings.embedding_provider)
    if settings.embedding_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for openai embedding provider")
        return OpenAIEmbeddingProvider(
            api_key=settings.openai_api_key,
            model=settings.openai_embedding_model,
            dimensions=settings.openai_embedding_dimensions,
        )
    if settings.embedding_provider == "mock":
        return MockEmbeddingProvider()
    raise ValueError(f"Unsupported POLICY_EMBEDDING_PROVIDER: {settings.embedding_provider}")


def build_vector_store(settings: PolicyIndexingSettings):
    logger.info("Policy indexing vector store=%s", settings.vector_store)
    if settings.vector_store == "pinecone":
        if not settings.pinecone_api_key:
            raise ValueError("PINECONE_API_KEY is required for pinecone vector store")
        return PineconePolicyStore(
            api_key=settings.pinecone_api_key,
            namespace=settings.pinecone_namespace,
            index_host=settings.pinecone_index_host,
            index_name=settings.pinecone_index_name,
        )
    if settings.vector_store == "qdrant":
        return QdrantPolicyStore()
    if settings.vector_store == "memory":
        return _memory_store
    raise ValueError(f"Unsupported POLICY_VECTOR_STORE: {settings.vector_store}")
