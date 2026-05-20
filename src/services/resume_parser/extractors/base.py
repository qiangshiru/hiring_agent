from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class ExtractionResult(Generic[T]):
    data: T | None
    confidence: float = 0.0
    source_text: str | None = None
    error: str | None = None


class ExtractionError(Exception):
    pass


class BaseExtractor(ABC, Generic[T]):
    @abstractmethod
    def extract(self, text: str) -> T:
        raise NotImplementedError

    def _calculate_confidence(self, value: T | None, source_length: int) -> float:
        if value is None:
            return 0.0
        if isinstance(value, str) and not value.strip():
            return 0.0
        if isinstance(value, list) and len(value) == 0:
            return 0.0
        base_confidence = min(1.0, source_length / 100)
        return max(0.3, base_confidence)


class RuleBasedExtractor(BaseExtractor[T]):
    pass


class LLMBasedExtractor(BaseExtractor[T]):
    pass


class HybridExtractor(BaseExtractor[T]):
    pass
