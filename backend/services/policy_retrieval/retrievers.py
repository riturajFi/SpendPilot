from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class PolicyChunk:
    chunk_id: str
    text: str


class PolicyRetriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, top_k: int) -> list[PolicyChunk]:
        raise NotImplementedError
