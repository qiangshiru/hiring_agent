from src.services.evaluation.evaluators.base import BaseEvaluator
from src.schemas.evaluation import (
    DimensionEvaluation,
    EvidenceItem,
    EvaluationLevel,
    InterviewRecord,
)


class SystemDesignEvaluator(BaseEvaluator):
    @property
    def dimension_name(self) -> str:
        return "系统设计"

    def evaluate(self, interview_record: InterviewRecord) -> DimensionEvaluation:
        evidence_list = []
        design_score = 0.0
        design_turn_count = 0

        for turn in interview_record.turns:
            if turn.question_type == "system_design":
                design_turn_count += 1
                evidence_list.append(
                    EvidenceItem(
                        source=f"面试-{turn.turn_id}",
                        content=f"系统设计问题: {turn.question[:50]}...",
                    )
                )
                if turn.answer_quality in ["excellent", "good"]:
                    design_score += 3.0
                elif turn.answer_quality == "fair":
                    design_score += 1.5
                else:
                    design_score += 0.5

        if design_turn_count == 0:
            return self._create_evaluation(
                level=EvaluationLevel.弱,
                score=3.0,
                evidence=evidence_list,
                comment="没有系统设计问题的回答",
            )

        avg_score = design_score / design_turn_count
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
            comment=f"基于{design_turn_count}个系统设计问题的回答评估",
        )
