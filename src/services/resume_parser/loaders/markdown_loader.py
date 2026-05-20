from pathlib import Path
from typing import BinaryIO

from src.services.resume_parser.loaders.base import (
    BaseDocumentLoader,
    CorruptedFileError,
    RawDocument,
)


class MarkdownLoader(BaseDocumentLoader):
    supported_extensions = [".md", ".txt"]

    def load(self, file_path: str | Path) -> RawDocument:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if not path.is_file():
            raise CorruptedFileError(f"Not a file: {file_path}")

        try:
            content = path.read_text(encoding="utf-8")
            if not content.strip():
                raise CorruptedFileError(f"File appears to be empty: {file_path}")

            line_count = len(content.splitlines())
            return RawDocument(
                content=content,
                file_name=path.name,
                file_type="markdown" if path.suffix == ".md" else "text",
                metadata={"line_count": line_count},
            )
        except UnicodeDecodeError:
            try:
                content = path.read_text(encoding="gbk")
                return RawDocument(
                    content=content,
                    file_name=path.name,
                    file_type="markdown" if path.suffix == ".md" else "text",
                    metadata={"encoding": "gbk"},
                )
            except Exception as exc:
                raise CorruptedFileError(f"Failed to decode file with any encoding: {exc}")
        except Exception as exc:
            raise CorruptedFileError(f"Failed to load file: {exc}")

    def load_from_stream(self, stream: BinaryIO, file_name: str) -> RawDocument:
        try:
            content = stream.read().decode("utf-8")
            if not content.strip():
                raise CorruptedFileError("Stream appears to be empty")

            return RawDocument(
                content=content,
                file_name=file_name,
                file_type="markdown" if file_name.endswith(".md") else "text",
            )
        except UnicodeDecodeError:
            try:
                stream.seek(0)
                content = stream.read().decode("gbk")
                return RawDocument(
                    content=content,
                    file_name=file_name,
                    file_type="markdown" if file_name.endswith(".md") else "text",
                    metadata={"encoding": "gbk"},
                )
            except Exception as exc:
                raise CorruptedFileError(f"Failed to decode stream with any encoding: {exc}")
        except Exception as exc:
            raise CorruptedFileError(f"Failed to load from stream: {exc}")
