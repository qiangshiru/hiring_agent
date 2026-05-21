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


class OverPackagingDetector(BaseRiskDetector):
    @property
    def risk_type(self) -> RiskType:
        return RiskType.过度包装

    def detect(
        self,
        interview_record: InterviewRecord,
        resume: Optional[ResumeParseResult] = None,
    ) -> Optional[RiskItem]:
        evidence_list = []

        # 检查回答中是否有大量空泛词汇
        buzzwords = [
            "赋能", "生态", "闭环", "抓手", "打法",
            "落地", "闭环", "链路", "协同", "沉淀"
        ]
        buzzword_count = 0
        total_answer_len = 0

        for turn in interview_record.turns:
            answer_lower = turn.answer.lower()
            total_answer_len += len(answer_lower)
            for word in buzzwords:
                if word in answer_lower:
                    buzzword_count += 1
                    evidence_list.append(
                        EvidenceItem(
                            source=f"面试-{turn.turn_id}",
                            content=f"回答中包含空泛词汇: {word}",
                        )
                    )

        buzzword_ratio = buzzword_count / max(total_answer_len, 1) * 100

        if buzzword_ratio > 1.0 and len(evidence_list) >= 3:
            return self._create_risk(
                level=RiskLevel.中,
                description="回答中空泛词汇比例较高，可能存在过度包装",
                evidence=evidence_list,
                confidence=0.6,
            )

        return None
