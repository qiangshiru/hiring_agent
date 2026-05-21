from typing import Optional

from src.services.risk_detection.detectors.base import BaseRiskDetector
from src.schemas.evaluation import (
    RiskItem,
    EvidenceItem,
    RiskType,
    RiskLevel,
    InterviewRecord,
)
from src.schemas.resume import ResumeParseResult


class RoteLearningDetector(BaseRiskDetector):
    @property
    def risk_type(self) -> RiskType:
        return RiskType.死记硬背

    def detect(
        self,
        interview_record: InterviewRecord,
        resume: Optional[ResumeParseResult] = None,
    ) -> Optional[RiskItem]:
        evidence_list = []
        follow_up_failure_count = 0

        # 检查追问问题的回答情况
        for turn in interview_record.turns:
            if turn.question_type == "follow_up" and turn.answer_quality in [
                "poor",
                "no_answer",
            ]:
                follow_up_failure_count += 1
                evidence_list.append(
                    EvidenceItem(
                        source=f"面试-{turn.turn_id}",
                        content=f"追问问题回答较差: {turn.question[:50]}...",
                    )
                )

        # 死记硬背特征：基础问题回答好但追问差
        if follow_up_failure_count >= 2:
            return self._create_risk(
                level=RiskLevel.中,
                description=f"追问问题中有{follow_up_failure_count}个回答较差，可能存在死记硬背",
                evidence=evidence_list,
                confidence=0.65,
            )

        return None
