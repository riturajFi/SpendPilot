from logging import getLogger

from backend.services.policy_indexing.contracts import (
    EmbeddingProvider,
    PolicyChunker,
    PolicyDocument,
    PolicyVectorStore,
)

logger = getLogger(__name__)


class PolicyIndexingService:
    def __init__(
        self,
        chunker: PolicyChunker,
        embedding_provider: EmbeddingProvider,
        vector_store: PolicyVectorStore,
    ) -> None:
        self.chunker = chunker
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    def index_policy(self, document: PolicyDocument) -> None:
        logger.info("Policy index start policy_id=%s", document.policy_id)
        chunks = self.chunker.chunk(document.policy_id, document.title, document.content)
        logger.info("Policy chunked policy_id=%s chunks=%s", document.policy_id, len(chunks))
        embeddings = self.embedding_provider.embed_texts([chunk.text for chunk in chunks])
        self.vector_store.upsert_chunks(document.policy_id, document.title, chunks, embeddings)
        logger.info("Policy index success policy_id=%s", document.policy_id)

    def reindex_policy(self, document: PolicyDocument) -> None:
        logger.info("Policy reindex start policy_id=%s", document.policy_id)
        self.vector_store.delete_policy_chunks(document.policy_id)
        self.index_policy(document)

    def delete_policy_index(self, policy_id: int) -> None:
        logger.info("Policy index delete start policy_id=%s", policy_id)
        self.vector_store.delete_policy_chunks(policy_id)
        logger.info("Policy index delete success policy_id=%s", policy_id)
