import hashlib
from logging import getLogger

from backend.services.policy_indexing.contracts import EmbeddingProvider

logger = getLogger(__name__)


class MockEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dimensions: int = 8) -> None:
        self.dimensions = dimensions

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        logger.info("MockEmbeddingProvider embed count=%s dims=%s", len(texts), self.dimensions)
        embeddings: list[list[float]] = []
        for text in texts:
            digest = hashlib.sha256(text.encode("utf-8")).digest()
            vector = [round(byte / 255, 6) for byte in digest[: self.dimensions]]
            embeddings.append(vector)
        return embeddings


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        dimensions: int | None = None,
    ) -> None:
        from openai import OpenAI

        self.model = model
        self.dimensions = dimensions
        self.client = OpenAI(api_key=api_key)
        logger.info(
            "OpenAIEmbeddingProvider initialized model=%s dimensions=%s",
            self.model,
            self.dimensions or "default",
        )

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            logger.info("OpenAIEmbeddingProvider embed skipped empty text list")
            return []

        params: dict = {
            "model": self.model,
            "input": texts,
            "encoding_format": "float",
        }
        if self.dimensions is not None:
            params["dimensions"] = self.dimensions

        logger.info("OpenAIEmbeddingProvider embed start count=%s", len(texts))
        response = self.client.embeddings.create(**params)
        embeddings = [item.embedding for item in response.data]
        logger.info(
            "OpenAIEmbeddingProvider embed success count=%s dims=%s",
            len(embeddings),
            len(embeddings[0]) if embeddings else 0,
        )
        return embeddings
