"""面试评估服务。

面试结束后，对候选人的面试记录进行多维度综合评审。
涵盖技术深度、系统设计、工程能力、沟通表达、真实性五个评估维度，
各维度独立评分后加权汇总得出综合评分，并自动提取候选人的优势和不足。
"""

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
    """面试评估服务核心类。

    通过 5 个维度评估器对面试记录进行独立评分，按预设权重
    （技术深度 30%、系统设计 20%、工程能力 20%、沟通表达 15%、真实性 15%）
    计算综合评分，并归纳优势和不足。
    """

    def __init__(self):
        self.evaluators = [
            TechDepthEvaluator(),
            CommunicationEvaluator(),
            AuthenticityEvaluator(),
            SystemDesignEvaluator(),
            EngineeringEvaluator(),
        ]

    def evaluate(self, interview_record: InterviewRecord) -> EvaluationResult:
        """对面试记录执行多维度评估，返回综合评分和优劣势分析。

        Args:
            interview_record: 面试记录

        Returns:
            评估结果，包含各维度评分、综合评分、优势和不足
        """
        evaluations = {}
        for evaluator in self.evaluators:
            dimension_eval = evaluator.evaluate(interview_record)
            evaluations[dimension_eval.dimension] = dimension_eval

        # 计算综合评分（各维度分数 * 权重 * 10 后求和，最终映射到 0-100 区间）
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

        # 提取优势和不足：评估等级为"强"的维度列入优势，"弱"的列入不足
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
