from pathlib import Path
from typing import BinaryIO

from src.services.resume_parser.loaders.base import (
    BaseDocumentLoader,
    CorruptedFileError,
    RawDocument,
    UnsupportedFormatError,
)


class PDFLoader(BaseDocumentLoader):
    supported_extensions = [".pdf"]

    def load(self, file_path: str | Path) -> RawDocument:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if not path.is_file():
            raise CorruptedFileError(f"Not a file: {file_path}")

        try:
            import pypdf

            reader = pypdf.PdfReader(str(path))
            text_parts: list[str] = []
            for page in reader.pages:
                text_parts.append(page.extract_text())

            content = "\n".join(text_parts)
            if not content.strip():
                raise CorruptedFileError(f"PDF appears to be empty or scanned: {file_path}")

            return RawDocument(
                content=content,
                file_name=path.name,
                file_type="pdf",
                metadata={"page_count": len(reader.pages)},
            )
        except ImportError:
            raise CorruptedFileError("pypdf is required to load PDF files")
        except Exception as exc:
            raise CorruptedFileError(f"Failed to load PDF: {exc}")

    def load_from_stream(self, stream: BinaryIO, file_name: str) -> RawDocument:
        try:
            import pypdf

            reader = pypdf.PdfReader(stream)
            text_parts: list[str] = []
            for page in reader.pages:
                text_parts.append(page.extract_text())

            content = "\n".join(text_parts)
            if not content.strip():
                raise CorruptedFileError("PDF appears to be empty or scanned")

            return RawDocument(
                content=content,
                file_name=file_name,
                file_type="pdf",
                metadata={"page_count": len(reader.pages)},
            )
        except ImportError:
            raise CorruptedFileError("pypdf is required to load PDF files")
        except Exception as exc:
            raise CorruptedFileError(f"Failed to load PDF from stream: {exc}")
