from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    text: str


@dataclass(frozen=True)
class PolicyDocument:
    policy_id: int
    title: str
    content: str


class PolicyChunker(ABC):
    @abstractmethod
    def chunk(self, policy_id: int, title: str, content: str) -> list[Chunk]:
        raise NotImplementedError


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class PolicyVectorStore(ABC):
    @abstractmethod
    def upsert_chunks(
        self,
        policy_id: int,
        title: str,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_policy_chunks(self, policy_id: int) -> None:
        raise NotImplementedError
