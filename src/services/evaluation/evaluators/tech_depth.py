from src.services.evaluation.evaluators.base import BaseEvaluator
from src.schemas.evaluation import (
    DimensionEvaluation,
    EvidenceItem,
    EvaluationLevel,
    InterviewRecord,
)


class TechDepthEvaluator(BaseEvaluator):
    @property
    def dimension_name(self) -> str:
        return "技术深度"

    def evaluate(self, interview_record: InterviewRecord) -> DimensionEvaluation:
        evidence_list = []
        depth_score = 0.0
        deep_turn_count = 0

        for turn in interview_record.turns:
            if turn.question_type in ["system_design", "deep_dive", "tradeoff"]:
                evidence_list.append(
                    EvidenceItem(
                        source=f"面试-{turn.turn_id}",
                        content=f"问题: {turn.question[:50]}... | 回答质量: {turn.answer_quality}",
                    )
                )
                if turn.answer_quality in ["excellent", "good"]:
                    depth_score += 3.0
                    deep_turn_count += 1
                elif turn.answer_quality == "fair":
                    depth_score += 1.5
                    deep_turn_count += 1

        if deep_turn_count == 0:
            return self._create_evaluation(
                level=EvaluationLevel.弱,
                score=3.0,
                evidence=evidence_list,
                comment="缺乏深度技术问题的回答",
            )

        avg_score = depth_score / deep_turn_count
        if avg_score >= 2.5:
            level = EvaluationLevel.强
        elif avg_score >= 1.5:
            level = EvaluationLevel.中
        else:
            level = EvaluationLevel.弱

        return self._create_evaluation(
            level=level,
            score=avg_score * 2.0,
            evidence=evidence_list,
            comment=f"基于{deep_turn_count}个深度技术问题的回答评估",
        )
