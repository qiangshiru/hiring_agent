"""候选人风险检测服务。

在面试评估完成后，对候选人进行多维度的风险筛查，检测潜在问题：
项目履历造假、过度包装、死记硬背、工作不稳定等风险点。
综合各检测器的结果，输出整体的风险等级和风险总结报告。
"""

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
    """候选人风险检测服务核心类。

    通过 4 个风险检测器（项目造假、过度包装、死记硬背、工作不稳定）
    对面试记录和简历进行并行检测，综合所有风险项得出总体风险等级。
    风险等级取所有检测项中的最高级别（无 < 低 < 中 < 高）。
    """

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
        """对候选人执行多维度风险检测。

        Args:
            interview_record: 面试记录
            resume: 候选人简历（可选，用于交叉验证）

        Returns:
            风险检测结果，包含各风险项、总体风险等级和风险总结
        """
        risks: List[RiskItem] = []

        for detector in self.detectors:
            risk = detector.detect(interview_record, resume)
            if risk:
                risks.append(risk)

        # 计算总体风险等级：取所有检测项中的最高风险级别
        overall_risk = self._calculate_overall_risk(risks)

        # 生成风险总结：汇总所有风险类型及对应等级的描述文本
        risk_summary = self._generate_summary(risks, overall_risk)

        return RiskDetectionResult(
            risks=risks,
            overall_risk_level=overall_risk,
            risk_summary=risk_summary,
        )

    def _calculate_overall_risk(self, risks: List[RiskItem]) -> RiskLevel:
        """取所有风险项中的最高风险等级作为整体风险等级。"""
        if not risks:
            return RiskLevel.无

        # 找出最高风险等级（无 < 低 < 中 < 高）
        max_level = RiskLevel.无
        level_order = [RiskLevel.无, RiskLevel.低, RiskLevel.中, RiskLevel.高]

        for risk in risks:
            current_idx = level_order.index(risk.risk_level)
            max_idx = level_order.index(max_level)
            if current_idx > max_idx:
                max_level = risk.risk_level

        return max_level

    def _generate_summary(self, risks: List[RiskItem], overall_risk: RiskLevel) -> str:
        """生成风险总结文本，汇总所有检测到的风险类型和等级。"""
        if not risks:
            return "未检测到明显风险"

        risk_descriptions = [f"{r.risk_type.value} (风险等级: {r.risk_level.value})" for r in risks]
        return f"检测到以下风险: {', '.join(risk_descriptions)}"
