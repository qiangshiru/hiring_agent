from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO


@dataclass
class RawDocument:
    content: str
    file_name: str
    file_type: str
    metadata: dict | None = None


class LoaderError(Exception):
    pass


class UnsupportedFormatError(LoaderError):
    pass


class CorruptedFileError(LoaderError):
    pass


class BaseDocumentLoader(ABC):
    supported_extensions: list[str] = []

    @abstractmethod
    def load(self, file_path: str | Path) -> RawDocument:
        raise NotImplementedError

    @abstractmethod
    def load_from_stream(self, stream: BinaryIO, file_name: str) -> RawDocument:
        raise NotImplementedError

    @classmethod
    def supports(cls, file_path: str | Path) -> bool:
        ext = Path(file_path).suffix.lower()
        return ext in cls.supported_extensions


class DocumentLoaderRegistry:
    def __init__(self) -> None:
        self._loaders: dict[str, BaseDocumentLoader] = {}

    def register(self, extension: str, loader: BaseDocumentLoader) -> None:
        ext = extension.lower()
        if not ext.startswith("."):
            ext = f".{ext}"
        self._loaders[ext] = loader

    def get_loader(self, file_path: str | Path) -> BaseDocumentLoader:
        ext = Path(file_path).suffix.lower()
        if ext not in self._loaders:
            raise UnsupportedFormatError(f"Unsupported file format: {ext}")
        return self._loaders[ext]

    def load(self, file_path: str | Path) -> RawDocument:
        loader = self.get_loader(file_path)
        return loader.load(file_path)


def create_default_registry() -> DocumentLoaderRegistry:
    from src.services.resume_parser.loaders import (
        DOCXLoader,
        MarkdownLoader,
        PDFLoader,
    )

    registry = DocumentLoaderRegistry()
    registry.register(".pdf", PDFLoader())
    registry.register(".docx", DOCXLoader())
    registry.register(".md", MarkdownLoader())
    registry.register(".txt", MarkdownLoader())
    return registry
