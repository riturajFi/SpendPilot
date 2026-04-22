from abc import ABC, abstractmethod
from pathlib import Path
from uuid import uuid4


class RawArtifactStore(ABC):
    @abstractmethod
    def save_file(self, content: bytes, file_name: str) -> str:
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
