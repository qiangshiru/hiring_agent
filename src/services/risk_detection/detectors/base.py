from abc import ABC, abstractmethod
from typing import List, Optional

from src.schemas.evaluation import (
    RiskItem,
    EvidenceItem,
    RiskType,
    RiskLevel,
    InterviewRecord,
)
from src.schemas.resume import ResumeParseResult


class BaseRiskDetector(ABC):
    @property
    @abstractmethod
    def risk_type(self) -> RiskType:
        pass

    @abstractmethod
    def detect(
        self,
        interview_record: InterviewRecord,
        resume: Optional[ResumeParseResult] = None,
    ) -> Optional[RiskItem]:
        pass

    def _create_risk(
        self,
        level: RiskLevel,
        description: str,
        evidence: List[EvidenceItem],
        confidence: float = 0.7,
    ) -> RiskItem:
        return RiskItem(
            risk_type=self.risk_type,
            risk_level=level,
            description=description,
            evidence=evidence,
            confidence=confidence,
        )
