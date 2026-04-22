from abc import ABC, abstractmethod


class DocumentParser(ABC):
    @abstractmethod
    def parse(self, file_bytes: bytes) -> str:
        raise NotImplementedError


class DocumentParserFactory(ABC):
    @abstractmethod
    def get_parser(self, file_type: str) -> DocumentParser:
        raise NotImplementedError


class PlainTextDocumentParser(DocumentParser):
    def parse(self, file_bytes: bytes) -> str:
        return file_bytes.decode("utf-8")


class SimpleDocumentParserFactory(DocumentParserFactory):
    def __init__(self) -> None:
        self._supported_file_types = {"txt", "csv", "md", "json"}
        self._parser = PlainTextDocumentParser()

    def get_parser(self, file_type: str) -> DocumentParser:
        normalized_file_type = file_type.lower()
        if normalized_file_type not in self._supported_file_types:
            raise ValueError(f"Unsupported document file type: {file_type}")
        return self._parser
