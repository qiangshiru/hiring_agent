from src.services.evaluation.evaluators.base import BaseEvaluator
from src.schemas.evaluation import (
    DimensionEvaluation,
    EvidenceItem,
    EvaluationLevel,
    InterviewRecord,
)


class AuthenticityEvaluator(BaseEvaluator):
    @property
    def dimension_name(self) -> str:
        return "真实性"

    def evaluate(self, interview_record: InterviewRecord) -> DimensionEvaluation:
        evidence_list = []
        consistency_score = 8.0
        contradiction_count = 0

        # 简单检查回答的一致性
        answers = [turn.answer.strip().lower() for turn in interview_record.turns]
        keywords = set()
        for answer in answers:
            if len(answer) > 0:
                words = answer.split()
                keywords.update(words[:10])

        # 检查回答的丰富度
        avg_answer_len = sum(len(a) for a in answers) / max(len(answers), 1)
        if avg_answer_len < 30:
            consistency_score -= 3.0
            evidence_list.append(
                EvidenceItem(
                    source="整体评估",
                    content=f"平均回答长度较短 ({avg_answer_len:.1f} 字)",
                )
            )

        # 检查回答质量的一致性
        quality_levels = [turn.answer_quality for turn in interview_record.turns]
        if len(set(quality_levels)) > 2:
            consistency_score -= 2.0
            evidence_list.append(
                EvidenceItem(
                    source="整体评估",
                    content="回答质量波动较大",
                )
            )

        if consistency_score >= 7.0:
            level = EvaluationLevel.强
        elif consistency_score >= 4.0:
            level = EvaluationLevel.中
        else:
            level = EvaluationLevel.弱

        return self._create_evaluation(
            level=level,
            score=max(consistency_score, 1.0),
            evidence=evidence_list,
            comment=f"基于回答一致性和丰富度的真实性评估",
        )
