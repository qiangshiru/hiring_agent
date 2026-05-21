from typing import Optional

from src.schemas.evaluation import (
    InterviewRecord,
    RiskDetectionResult,
    EvaluationResult,
    EvaluationReport,
)
from src.schemas.resume import ResumeParseResult
from src.services.evaluation import EvaluationService, ReportGenerator
from src.services.risk_detection import RiskDetectionService


class RiskAgent:
    def __init__(self):
        self.evaluation_service = EvaluationService()
        self.risk_service = RiskDetectionService()
        self.report_generator = ReportGenerator()

    def run_full_analysis(
        self,
        interview_record: InterviewRecord,
        resume: Optional[ResumeParseResult] = None,
        candidate_name: str = "候选人",
    ) -> EvaluationReport:
        # 执行评价
        evaluation_result = self.evaluation_service.evaluate(interview_record)

        # 执行风险检测
        risk_result = self.risk_service.detect(interview_record, resume)

        # 生成报告
        report = self.report_generator.generate(
            candidate_name=candidate_name,
            evaluation_result=evaluation_result,
            risk_result=risk_result,
        )

        return report
