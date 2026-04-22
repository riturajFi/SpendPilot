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


class LocalRawArtifactStore(RawArtifactStore):
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path(__file__).resolve().parent.parent.parent / "storage" / "raw"

    def save_file(self, content: bytes, file_name: str) -> str:
        self.root.mkdir(parents=True, exist_ok=True)
        suffix = Path(file_name).suffix
        file_key = f"{uuid4().hex}{suffix}"
        destination = self.root / file_key
        destination.write_bytes(content)
        return file_key

    def read_file(self, file_key: str) -> bytes:
        return (self.root / file_key).read_bytes()


class LocalParsedArtifactStore(ParsedArtifactStore):
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path(__file__).resolve().parent.parent.parent / "storage" / "parsed"

    def save_text(self, document_id: int, text: str) -> str:
        self.root.mkdir(parents=True, exist_ok=True)
        file_key = f"{document_id}.txt"
        destination = self.root / file_key
        destination.write_text(text, encoding="utf-8")
        return file_key
