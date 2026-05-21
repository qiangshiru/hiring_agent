from src.services.evaluation.evaluators.base import BaseEvaluator
from src.schemas.evaluation import (
    DimensionEvaluation,
    EvidenceItem,
    EvaluationLevel,
    InterviewRecord,
)


class CommunicationEvaluator(BaseEvaluator):
    @property
    def dimension_name(self) -> str:
        return "沟通表达"

    def evaluate(self, interview_record: InterviewRecord) -> DimensionEvaluation:
        evidence_list = []
        total_quality_score = 0.0
        answer_count = 0

        for turn in interview_record.turns:
            answer_len = len(turn.answer.strip())
            quality_score = self._score_answer_quality(turn.answer_quality)
            total_quality_score += quality_score
            answer_count += 1

            evidence_list.append(
                EvidenceItem(
                    source=f"面试-{turn.turn_id}",
                    content=f"回答长度: {answer_len} 字 | 质量: {turn.answer_quality}",
                )
            )

        if answer_count == 0:
            return self._create_evaluation(
                level=EvaluationLevel.弱,
                score=3.0,
                evidence=evidence_list,
                comment="没有回答记录",
            )

        avg_score = total_quality_score / answer_count
        if avg_score >= 3.5:
            level = EvaluationLevel.强
        elif avg_score >= 2.0:
            level = EvaluationLevel.中
        else:
            level = EvaluationLevel.弱

        return self._create_evaluation(
            level=level,
            score=avg_score * 2.0,
            evidence=evidence_list,
            comment=f"基于{answer_count}个回答的沟通质量评估",
        )

    def _score_answer_quality(self, quality: str) -> float:
        quality_scores = {
            "excellent": 4.0,
            "good": 3.0,
            "fair": 2.0,
            "poor": 1.0,
            "no_answer": 0.0,
        }
        return quality_scores.get(quality, 1.0)
