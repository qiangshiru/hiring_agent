from typing import List, Optional

from src.schemas.evaluation import (
    RiskDetectionResult,
    RiskItem,
    RiskLevel,
    InterviewRecord,
)
from src.schemas.resume import ResumeParseResult
from src.services.risk_detection.detectors.project_fraud import ProjectFraudDetector
from src.services.risk_detection.detectors.over_packaging import OverPackagingDetector
from src.services.risk_detection.detectors.rote_learning import RoteLearningDetector
from src.services.risk_detection.detectors.instability import InstabilityDetector


class RiskDetectionService:
    def __init__(self):
        self.detectors = [
            ProjectFraudDetector(),
            OverPackagingDetector(),
            RoteLearningDetector(),
            InstabilityDetector(),
        ]

    def detect(
        self,
        interview_record: InterviewRecord,
        resume: Optional[ResumeParseResult] = None,
    ) -> RiskDetectionResult:
        risks: List[RiskItem] = []

        for detector in self.detectors:
            risk = detector.detect(interview_record, resume)
            if risk:
                risks.append(risk)

        # 计算总体风险等级
        overall_risk = self._calculate_overall_risk(risks)

        # 生成风险总结
        risk_summary = self._generate_summary(risks, overall_risk)

        return RiskDetectionResult(
            risks=risks,
            overall_risk_level=overall_risk,
            risk_summary=risk_summary,
        )

    def _calculate_overall_risk(self, risks: List[RiskItem]) -> RiskLevel:
        if not risks:
            return RiskLevel.无

        # 找出最高风险等级
        max_level = RiskLevel.无
        level_order = [RiskLevel.无, RiskLevel.低, RiskLevel.中, RiskLevel.高]

        for risk in risks:
            current_idx = level_order.index(risk.risk_level)
            max_idx = level_order.index(max_level)
            if current_idx > max_idx:
                max_level = risk.risk_level

        return max_level

    def _generate_summary(self, risks: List[RiskItem], overall_risk: RiskLevel) -> str:
        if not risks:
            return "未检测到明显风险"

        risk_descriptions = [f"{r.risk_type.value} (风险等级: {r.risk_level.value})" for r in risks]
        return f"检测到以下风险: {', '.join(risk_descriptions)}"
