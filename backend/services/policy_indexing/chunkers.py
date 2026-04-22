from backend.services.policy_indexing.contracts import Chunk, PolicyChunker


class FixedSizeChunker(PolicyChunker):
    def __init__(self, chunk_size: int = 500) -> None:
        self.chunk_size = chunk_size

    def chunk(self, policy_id: int, title: str, content: str) -> list[Chunk]:
        normalized = " ".join(content.split())
        if not normalized:
            return []

        chunks: list[Chunk] = []
        for index, start in enumerate(range(0, len(normalized), self.chunk_size), start=1):
            text = normalized[start : start + self.chunk_size]
            chunks.append(Chunk(chunk_id=f"{policy_id}:{index}", text=text))
        return chunks
