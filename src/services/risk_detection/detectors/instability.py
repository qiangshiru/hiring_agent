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


class InstabilityDetector(BaseRiskDetector):
    @property
    def risk_type(self) -> RiskType:
        return RiskType.不稳定

    def detect(
        self,
        interview_record: InterviewRecord,
        resume: Optional[ResumeParseResult] = None,
    ) -> Optional[RiskItem]:
        evidence_list = []

        # 检查回答质量的波动
        quality_scores = {
            "excellent": 4,
            "good": 3,
            "fair": 2,
            "poor": 1,
            "no_answer": 0,
        }
        scores = []
        for turn in interview_record.turns:
            scores.append(quality_scores.get(turn.answer_quality, 1))

        if len(scores) >= 3:
            # 计算波动程度
            max_score = max(scores)
            min_score = min(scores)
            score_range = max_score - min_score

            if score_range >= 3:
                evidence_list.append(
                    EvidenceItem(
                        source="整体评估",
                        content=f"回答质量波动较大 (最高{max_score}, 最低{min_score})",
                    )
                )

            # 检查是否有连续差回答
            consecutive_poor = 0
            for score in scores:
                if score <= 1:
                    consecutive_poor += 1
                    if consecutive_poor >= 2:
                        evidence_list.append(
                            EvidenceItem(
                                source="整体评估",
                                content="出现连续较差回答",
                            )
                        )
                        break
                else:
                    consecutive_poor = 0

        if len(evidence_list) > 0:
            return self._create_risk(
                level=RiskLevel.低,
                description="回答稳定性存在问题",
                evidence=evidence_list,
                confidence=0.5,
            )

        return None
