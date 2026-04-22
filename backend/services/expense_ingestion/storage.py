from abc import ABC, abstractmethod
from pathlib import Path
from uuid import uuid4


class RawArtifactStore(ABC):
    @abstractmethod
    def save_file(self, content: bytes, file_name: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def read_file(self, file_key: str) -> bytes:
        raise NotImplementedError


class ParsedArtifactStore(ABC):
    @abstractmethod
    def save_text(self, document_id: int, text: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def read_text(self, document_id: int) -> str:
        raise NotImplementedError


class _LocalArtifactStore:
    def __init__(self, root: Path) -> None:
        self.root = root

    def _ensure_root(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)


class LocalRawArtifactStore(_LocalArtifactStore, RawArtifactStore):
    def __init__(self, root: Path | None = None) -> None:
        super().__init__(
            root or Path(__file__).resolve().parent.parent.parent / "storage" / "raw"
        )

    def save_file(self, content: bytes, file_name: str) -> str:
        self._ensure_root()
        suffix = Path(file_name).suffix
        file_key = f"{uuid4().hex}{suffix}"
        destination = self.root / file_key
        destination.write_bytes(content)
        return file_key

    def read_file(self, file_key: str) -> bytes:
        return (self.root / file_key).read_bytes()


class LocalParsedArtifactStore(_LocalArtifactStore, ParsedArtifactStore):
    def __init__(self, root: Path | None = None) -> None:
        super().__init__(
            root or Path(__file__).resolve().parent.parent.parent / "storage" / "parsed"
        )

    def save_text(self, document_id: int, text: str) -> str:
        self._ensure_root()
        file_key = self._build_file_key(document_id)
        destination = self.root / file_key
        destination.write_text(text, encoding="utf-8")
        return file_key

    def read_text(self, document_id: int) -> str:
        file_key = self._build_file_key(document_id)
        return (self.root / file_key).read_text(encoding="utf-8")

    def _build_file_key(self, document_id: int) -> str:
        return f"{document_id}.txt"
