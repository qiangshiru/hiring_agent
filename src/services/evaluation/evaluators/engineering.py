from src.services.evaluation.evaluators.base import BaseEvaluator
from src.schemas.evaluation import (
    DimensionEvaluation,
    EvidenceItem,
    EvaluationLevel,
    InterviewRecord,
)


class EngineeringEvaluator(BaseEvaluator):
    @property
    def dimension_name(self) -> str:
        return "工程能力"

    def evaluate(self, interview_record: InterviewRecord) -> DimensionEvaluation:
        evidence_list = []
        eng_score = 0.0
        eng_turn_count = 0

        for turn in interview_record.turns:
            if turn.question_type in ["failure", "scenario", "tradeoff"]:
                eng_turn_count += 1
                evidence_list.append(
                    EvidenceItem(
                        source=f"面试-{turn.turn_id}",
                        content=f"工程实践问题: {turn.question[:50]}...",
                    )
                )
                if turn.answer_quality in ["excellent", "good"]:
                    eng_score += 3.0
                elif turn.answer_quality == "fair":
                    eng_score += 1.5
                else:
                    eng_score += 0.5

        if eng_turn_count == 0:
            return self._create_evaluation(
                level=EvaluationLevel.弱,
                score=3.0,
                evidence=evidence_list,
                comment="没有工程实践问题的回答",
            )

        avg_score = eng_score / eng_turn_count
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
            comment=f"基于{eng_turn_count}个工程实践问题的回答评估",
        )
