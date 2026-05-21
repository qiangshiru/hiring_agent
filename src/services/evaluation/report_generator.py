from src.schemas.evaluation import (
    EvaluationReport,
    EvaluationResult,
    RiskDetectionResult,
    RiskLevel,
)


class ReportGenerator:
    def generate(
        self,
        candidate_name: str,
        evaluation_result: EvaluationResult,
        risk_result: RiskDetectionResult,
    ) -> EvaluationReport:
        # 生成录用建议
        recommendation = self._get_hiring_recommendation(
            evaluation_result, risk_result
        )

        # 提取关键洞察
        key_insights = self._extract_key_insights(evaluation_result, risk_result)

        return EvaluationReport(
            candidate_name=candidate_name,
            evaluation_result=evaluation_result,
            risk_result=risk_result,
            hiring_recommendation=recommendation,
            key_insights=key_insights,
        )

    def _get_hiring_recommendation(
        self,
        evaluation_result: EvaluationResult,
        risk_result: RiskDetectionResult,
    ) -> str:
        score = evaluation_result.综合评分
        risk_level = risk_result.overall_risk_level

        if score >= 80.0 and risk_level == RiskLevel.无:
            return "强烈推荐"
        elif score >= 65.0 and risk_level in [RiskLevel.无, RiskLevel.低]:
            return "推荐"
        elif score >= 50.0 and risk_level != RiskLevel.高:
            return "谨慎推荐"
        else:
            return "不推荐"

    def _extract_key_insights(
        self,
        evaluation_result: EvaluationResult,
        risk_result: RiskDetectionResult,
    ) -> list:
        insights = []

        # 优势洞察
        for strength in evaluation_result.优势:
            insights.append(f"优势: {strength}")

        # 不足洞察
        for weakness in evaluation_result.不足:
            insights.append(f"待提升: {weakness}")

        # 风险洞察
        if risk_result.overall_risk_level != RiskLevel.无:
            insights.append(f"风险等级: {risk_result.overall_risk_level}")

        # 综合评分洞察
        insights.append(f"综合评分: {evaluation_result.综合评分:.1f}分")

        return insights
