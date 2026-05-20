from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.schemas.jd import JDParseResult
from src.schemas.resume import ResumeParseResult


@dataclass
class DimensionResult:
    score: float
    reason: str | None = None
    confidence: float = 1.0
    details: dict | None = None


class BaseDimensionScorer(ABC):
    def __init__(self, name: str, description: str, weight: float = 0.0) -> None:
        self.name = name
        self.description = description
        self.weight = weight

    @abstractmethod
    def score(
        self, jd: JDParseResult, resume: ResumeParseResult
    ) -> DimensionResult:
        raise NotImplementedError

    def _clamp_score(self, score: float) -> float:
        return max(0.0, min(100.0, score))

    def _calculate_confidence(
        self, jd: JDParseResult, resume: ResumeParseResult
    ) -> float:
        confidence = 1.0
        if not resume.姓名:
            confidence *= 0.8
        if not resume.技能:
            confidence *= 0.9
        return round(confidence, 3)
