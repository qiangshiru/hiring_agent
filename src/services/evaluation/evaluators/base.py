from abc import ABC, abstractmethod
from typing import List

from src.schemas.evaluation import (
    DimensionEvaluation,
    EvidenceItem,
    EvaluationLevel,
    InterviewRecord,
)


class BaseEvaluator(ABC):
    @property
    @abstractmethod
    def dimension_name(self) -> str:
        pass

    @abstractmethod
    def evaluate(self, interview_record: InterviewRecord) -> DimensionEvaluation:
        pass

    def _create_evaluation(
        self,
        level: EvaluationLevel,
        score: float,
        evidence: List[EvidenceItem],
        comment: str = "",
    ) -> DimensionEvaluation:
        return DimensionEvaluation(
            dimension=self.dimension_name,
            level=level,
            score=score,
            evidence=evidence,
            comment=comment,
        )
