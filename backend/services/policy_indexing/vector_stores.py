from dataclasses import dataclass
from logging import getLogger

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
