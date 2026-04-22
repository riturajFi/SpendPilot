from abc import ABC, abstractmethod
from dataclasses import dataclass

from backend.services.policy_indexing.contracts import EmbeddingProvider, PolicyVectorStore


@dataclass(frozen=True)
class PolicyChunk:
    chunk_id: str
    text: str


class PolicyRetriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, top_k: int) -> list[PolicyChunk]:
        raise NotImplementedError


class EmbeddingPolicyRetriever(PolicyRetriever):
    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: PolicyVectorStore,
    ) -> None:
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int) -> list[PolicyChunk]:
        embeddings = self.embedding_provider.embed_texts([query])
        if not embeddings:
            return []

        chunks = self.vector_store.query_similar_chunks(embedding=embeddings[0], top_k=top_k)
        return [PolicyChunk(chunk_id=chunk.chunk_id, text=chunk.text) for chunk in chunks]
