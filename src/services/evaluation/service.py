from typing import List

from src.schemas.evaluation import (
    EvaluationResult,
    InterviewRecord,
    EvaluationLevel,
)
from src.services.evaluation.evaluators.tech_depth import TechDepthEvaluator
from src.services.evaluation.evaluators.communication import CommunicationEvaluator
from src.services.evaluation.evaluators.authenticity import AuthenticityEvaluator
from src.services.evaluation.evaluators.system_design import SystemDesignEvaluator
from src.services.evaluation.evaluators.engineering import EngineeringEvaluator


class EvaluationService:
    def __init__(self):
        self.evaluators = [
            TechDepthEvaluator(),
            CommunicationEvaluator(),
            AuthenticityEvaluator(),
            SystemDesignEvaluator(),
            EngineeringEvaluator(),
        ]

    def evaluate(self, interview_record: InterviewRecord) -> EvaluationResult:
        evaluations = {}
        for evaluator in self.evaluators:
            dimension_eval = evaluator.evaluate(interview_record)
            evaluations[dimension_eval.dimension] = dimension_eval

        # 计算综合评分
        total_score = 0.0
        weights = {
            "技术深度": 0.30,
            "系统设计": 0.20,
            "工程能力": 0.20,
            "沟通表达": 0.15,
            "真实性": 0.15,
        }

        for dim_name, eval_result in evaluations.items():
            weight = weights.get(dim_name, 0.2)
            total_score += eval_result.score * weight * 10

        total_score = min(max(total_score, 0.0), 100.0)

        # 提取优势和不足
        strengths = []
        weaknesses = []
        for dim_name, eval_result in evaluations.items():
            if eval_result.level == EvaluationLevel.强:
                strengths.append(f"{dim_name}表现优秀")
            elif eval_result.level == EvaluationLevel.弱:
                weaknesses.append(f"{dim_name}需要提升")

        return EvaluationResult(
            技术深度=evaluations["技术深度"],
            沟通表达=evaluations["沟通表达"],
            真实性=evaluations["真实性"],
            系统设计=evaluations["系统设计"],
            工程能力=evaluations["工程能力"],
            综合评分=total_score,
            优势=strengths,
            不足=weaknesses,
        )
