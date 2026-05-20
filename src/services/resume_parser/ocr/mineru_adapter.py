from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO

from src.services.resume_parser.loaders.base import RawDocument


class OCRError(Exception):
    pass


class BaseOCRAdapter(ABC):
    @abstractmethod
    async def extract_text(self, file_path: str | Path) -> str:
        raise NotImplementedError

    @abstractmethod
    async def extract_text_from_stream(self, stream: BinaryIO, file_name: str) -> str:
        raise NotImplementedError


class MinerULocalAdapter(BaseOCRAdapter):
    def __init__(self, model_path: str | None = None) -> None:
        self._model_path = model_path
        self._initialized = False

    async def extract_text(self, file_path: str | Path) -> str:
        try:
            from magic_pdf.data.utils import img2pdf, pdf2imgs
            from magic_pdf.model.doc_extract_kit import ModelScopePipeline

            if not self._initialized:
                self._pipeline = ModelScopePipeline(self._model_path)
                self._initialized = True

            path = Path(file_path)
            if path.suffix.lower() == ".pdf":
                imgs = pdf2imgs(str(path))
                text_parts = []
                for img_bytes in imgs:
                    result = self._pipeline(img_bytes)
                    text_parts.append(result.get("text", ""))
                return "\n".join(text_parts)
            else:
                img_bytes = img2pdf(str(path))
                result = self._pipeline(img_bytes)
                return result.get("text", "")

        except ImportError:
            raise OCRError("magic-pdf is required for MinerU local mode")
        except Exception as exc:
            raise OCRError(f"MinerU local OCR failed: {exc}")

    async def extract_text_from_stream(self, stream: BinaryIO, file_name: str) -> str:
        try:
            import tempfile
            from magic_pdf.data.utils import img2pdf, pdf2imgs
            from magic_pdf.model.doc_extract_kit import ModelScopePipeline

            if not self._initialized:
                self._pipeline = ModelScopePipeline(self._model_path)
                self._initialized = True

            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file_name).suffix) as tmp:
                tmp.write(stream.read())
                tmp_path = tmp.name

            try:
                if Path(file_name).suffix.lower() == ".pdf":
                    imgs = pdf2imgs(tmp_path)
                    text_parts = []
                    for img_bytes in imgs:
                        result = self._pipeline(img_bytes)
                        text_parts.append(result.get("text", ""))
                    return "\n".join(text_parts)
                else:
                    img_bytes = img2pdf(tmp_path)
                    result = self._pipeline(img_bytes)
                    return result.get("text", "")
            finally:
                Path(tmp_path).unlink(missing_ok=True)

        except ImportError:
            raise OCRError("magic-pdf is required for MinerU local mode")
        except Exception as exc:
            raise OCRError(f"MinerU local OCR failed: {exc}")


class MinerUAPIAdapter(BaseOCRAdapter):
    def __init__(self, api_url: str, api_key: str | None = None) -> None:
        self._api_url = api_url.rstrip("/")
        self._api_key = api_key

    async def extract_text(self, file_path: str | Path) -> str:
        try:
            import httpx

            path = Path(file_path)
            with open(path, "rb") as f:
                files = {"file": (path.name, f.read(), self._get_mime_type(path))}
                headers = self._get_headers()

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self._api_url}/extract",
                        files=files,
                        headers=headers,
                        timeout=60.0,
                    )
                    response.raise_for_status()
                    result = response.json()
                    return result.get("text", "")

        except ImportError:
            raise OCRError("httpx is required for MinerU API mode")
        except Exception as exc:
            raise OCRError(f"MinerU API OCR failed: {exc}")

    async def extract_text_from_stream(self, stream: BinaryIO, file_name: str) -> str:
        try:
            import httpx

            files = {"file": (file_name, stream.read(), self._get_mime_type(Path(file_name)))}
            headers = self._get_headers()

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self._api_url}/extract",
                    files=files,
                    headers=headers,
                    timeout=60.0,
                )
                response.raise_for_status()
                result = response.json()
                return result.get("text", "")

        except ImportError:
            raise OCRError("httpx is required for MinerU API mode")
        except Exception as exc:
            raise OCRError(f"MinerU API OCR failed: {exc}")

    def _get_headers(self) -> dict[str, str]:
        headers = {}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    def _get_mime_type(self, path: Path) -> str:
        mime_types = {
            ".pdf": "application/pdf",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".tiff": "image/tiff",
        }
        return mime_types.get(path.suffix.lower(), "application/octet-stream")


class OCRFactory:
    @staticmethod
    def create(mode: str = "local", **kwargs) -> BaseOCRAdapter:
        if mode == "local":
            return MinerULocalAdapter(model_path=kwargs.get("model_path"))
        elif mode == "api":
            return MinerUAPIAdapter(
                api_url=kwargs["api_url"],
                api_key=kwargs.get("api_key"),
            )
        else:
            raise ValueError(f"Unknown OCR mode: {mode}")
