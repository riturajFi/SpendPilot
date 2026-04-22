from dataclasses import dataclass
from logging import getLogger
from math import sqrt

from backend.services.policy_indexing.contracts import Chunk, PolicyVectorStore

logger = getLogger(__name__)


@dataclass
class StoredChunk:
    policy_id: int
    chunk_id: str
    text: str
    title: str
    embedding: list[float]


class InMemoryPolicyStore(PolicyVectorStore):
    def __init__(self) -> None:
        self._chunks_by_policy: dict[int, list[StoredChunk]] = {}

    def upsert_chunks(
        self,
        policy_id: int,
        title: str,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> None:
        logger.info("InMemoryPolicyStore upsert policy_id=%s chunks=%s", policy_id, len(chunks))
        self._chunks_by_policy[policy_id] = [
            StoredChunk(
                policy_id=policy_id,
                chunk_id=chunk.chunk_id,
                text=chunk.text,
                title=title,
                embedding=embedding,
            )
            for chunk, embedding in zip(chunks, embeddings, strict=True)
        ]

    def delete_policy_chunks(self, policy_id: int) -> None:
        logger.info("InMemoryPolicyStore delete policy_id=%s", policy_id)
        self._chunks_by_policy.pop(policy_id, None)

    def get_policy_chunks(self, policy_id: int) -> list[StoredChunk]:
        return list(self._chunks_by_policy.get(policy_id, []))

    def query_similar_chunks(self, embedding: list[float], top_k: int) -> list[Chunk]:
        all_chunks = [
            stored_chunk
            for chunks in self._chunks_by_policy.values()
            for stored_chunk in chunks
        ]
        ranked_chunks = sorted(
            all_chunks,
            key=lambda stored_chunk: _cosine_similarity(embedding, stored_chunk.embedding),
            reverse=True,
        )
        return [
            Chunk(chunk_id=stored_chunk.chunk_id, text=stored_chunk.text)
            for stored_chunk in ranked_chunks[:top_k]
        ]


class PineconePolicyStore(PolicyVectorStore):
    def __init__(
        self,
        api_key: str,
        namespace: str = "policy-index",
        index_host: str | None = None,
        index_name: str | None = None,
    ) -> None:
        from pinecone import Pinecone

        if not index_host and not index_name:
            raise ValueError("index_host or index_name is required")

        self.namespace = namespace
        client = Pinecone(api_key=api_key)
        self.index = client.Index(host=index_host) if index_host else client.Index(index_name)
        logger.info(
            "PineconePolicyStore initialized namespace=%s target=%s",
            self.namespace,
            index_host or index_name,
        )

    def upsert_chunks(
        self,
        policy_id: int,
        title: str,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> None:
        if not chunks:
            logger.info("PineconePolicyStore upsert skipped policy_id=%s no chunks", policy_id)
            return

        vectors = [
            {
                "id": chunk.chunk_id,
                "values": embedding,
                "metadata": {
                    "policy_id": policy_id,
                    "chunk_id": chunk.chunk_id,
                    "text": chunk.text,
                    "title": title,
                },
            }
            for chunk, embedding in zip(chunks, embeddings, strict=True)
        ]
        dims = len(embeddings[0]) if embeddings else 0
        logger.info(
            "PineconePolicyStore upsert start policy_id=%s chunks=%s dims=%s namespace=%s",
            policy_id,
            len(chunks),
            dims,
            self.namespace,
        )
        self.index.upsert(vectors=vectors, namespace=self.namespace)
        logger.info(
            "PineconePolicyStore upsert success policy_id=%s chunks=%s",
            policy_id,
            len(chunks),
        )

    def delete_policy_chunks(self, policy_id: int) -> None:
        logger.info(
            "PineconePolicyStore delete start policy_id=%s namespace=%s",
            policy_id,
            self.namespace,
        )
        self.index.delete(
            filter={"policy_id": {"$eq": policy_id}},
            namespace=self.namespace,
        )
        logger.info("PineconePolicyStore delete success policy_id=%s", policy_id)

    def query_similar_chunks(self, embedding: list[float], top_k: int) -> list[Chunk]:
        logger.info(
            "PineconePolicyStore query start top_k=%s namespace=%s",
            top_k,
            self.namespace,
        )
        response = self.index.query(
            vector=embedding,
            top_k=top_k,
            namespace=self.namespace,
            include_metadata=True,
        )
        matches = getattr(response, "matches", None)
        if matches is None and isinstance(response, dict):
            matches = response.get("matches", [])
        matches = matches or []

        chunks: list[Chunk] = []
        for match in matches:
            metadata = _get_match_metadata(match)
            chunk_id = str(metadata.get("chunk_id", ""))
            text = str(metadata.get("text", ""))
            if chunk_id and text:
                chunks.append(Chunk(chunk_id=chunk_id, text=text))

        logger.info("PineconePolicyStore query success chunks=%s", len(chunks))
        return chunks


class QdrantPolicyStore(PolicyVectorStore):
    def __init__(self, *args, **kwargs) -> None:
        pass

    def upsert_chunks(
        self,
        policy_id: int,
        title: str,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> None:
        raise NotImplementedError("QdrantPolicyStore not implemented yet")

    def delete_policy_chunks(self, policy_id: int) -> None:
        raise NotImplementedError("QdrantPolicyStore not implemented yet")

    def query_similar_chunks(self, embedding: list[float], top_k: int) -> list[Chunk]:
        raise NotImplementedError("QdrantPolicyStore not implemented yet")


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0

    dot_product = sum(left_value * right_value for left_value, right_value in zip(left, right))
    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot_product / (left_norm * right_norm)


def _get_match_metadata(match) -> dict:
    if isinstance(match, dict):
        return match.get("metadata", {}) or {}
    return getattr(match, "metadata", {}) or {}
