"""候选人综合评分服务。

在筛选通过后，对候选人进行多维度量化评分，包括技术匹配度、AI 深度、
工程能力、学历、稳定性等 5 个维度。每个维度有独立的评分器，最终通过
加权求和得出总分，并根据阈值生成推荐等级（强烈推荐/推荐/可考虑/备选/不推荐）。
"""

from typing import Protocol

from src.schemas.jd import JDParseResult
from src.schemas.resume import ResumeParseResult
from src.schemas.scoring import DimensionWeights
from src.schemas.screening import DimensionScore, ScoringResult
from src.services.scoring.dimensions import (
    AIDepthScorer,
    BaseDimensionScorer,
    DimensionResult,
    EducationScorer,
    EngineeringScorer,
    StabilityScorer,
    TechMatchScorer,
)
from src.services.scoring.weights import DefaultWeights


class ScoringCache(Protocol):
    """评分结果缓存协议，定义缓存的读写接口。"""

    async def get(self, key: str) -> ScoringResult | None:
        raise NotImplementedError

    async def set(self, key: str, value: ScoringResult, ttl_seconds: int) -> None:
        raise NotImplementedError


class NullScoringCache:
    """空缓存实现（不使用缓存时回退到此实现）。"""
    async def get(self, key: str) -> ScoringResult | None:
        return None

    async def set(self, key: str, value: ScoringResult, ttl_seconds: int) -> None:
        return None


class ScoringService:
    """候选人综合评分服务核心类。

    通过多个维度评分器对候选人进行加权评分，每个维度的权重可动态调整。
    最终总分映射到推荐等级：>=85 强烈推荐、>=70 推荐、>=55 可考虑、
    >=40 备选、<40 不推荐。
    """

    def __init__(
        self,
        weights: DimensionWeights | None = None,
        dimensions: list[BaseDimensionScorer] | None = None,
        cache: ScoringCache | None = None,
    ) -> None:
        self._weights = weights or DefaultWeights.standard()
        self._cache = cache if cache is not None else NullScoringCache()

        if dimensions:
            self._dimensions = dimensions
        else:
            self._dimensions = [
                TechMatchScorer(),
                AIDepthScorer(),
                EngineeringScorer(),
                EducationScorer(),
                StabilityScorer(),
            ]

        self._update_dimension_weights()

    def _update_dimension_weights(self) -> None:
        """将权重配置同步到各维度评分器实例。"""
        weight_map = {
            "tech_match": self._weights.tech_match,
            "ai_depth": self._weights.ai_depth,
            "engineering": self._weights.engineering,
            "education": self._weights.education,
            "stability": self._weights.stability,
        }
        for dim in self._dimensions:
            if dim.name in weight_map:
                dim.weight = weight_map[dim.name]

    def score(
        self, jd: JDParseResult, resume: ResumeParseResult
    ) -> ScoringResult:
        """对候选人进行多维度加权评分，生成总分、各维度得分和推荐等级。

        Args:
            jd: 解析后的 JD 结果
            resume: 解析后的简历结果

        Returns:
            评分结果，包含总分、各维度分数、置信度和推荐等级
        """
        dimension_scores: list[DimensionScore] = []
        total_score = 0.0
        total_confidence = 0.0

        for dimension in self._dimensions:
            result = dimension.score(jd, resume)

            weighted_score = result.score * dimension.weight
            total_score += weighted_score
            total_confidence += result.confidence * dimension.weight

            dimension_scores.append(DimensionScore(
                name=dimension.name,
                score=round(result.score, 2),
                weight=dimension.weight,
                confidence=result.confidence,
                reason=result.reason,
                details=result.details,
            ))

        final_score = round(min(100.0, max(0.0, total_score)), 2)
        overall_confidence = round(total_confidence, 3)

        summary = self._generate_summary(final_score, dimension_scores)
        recommendation = self._generate_recommendation(final_score)

        return ScoringResult(
            total=final_score,
            dimensions=dimension_scores,
            overall_confidence=overall_confidence,
            summary=summary,
            recommendation=recommendation,
        )

    def _generate_summary(
        self, total: float, dimensions: list[DimensionScore]
    ) -> str:
        """生成评分摘要文本，包含总分及最高/最低维度信息。"""
        sorted_dims = sorted(dimensions, key=lambda d: d.score, reverse=True)
        top = sorted_dims[0]
        bottom = sorted_dims[-1]

        return (
            f"总分: {total:.0f}分 | "
            f"最高: {top.name}({top.score:.0f}) | "
            f"最低: {bottom.name}({bottom.score:.0f})"
        )

    def _generate_recommendation(self, total: float) -> str:
        """根据总分阈值映射到对应的推荐等级文案。"""
        if total >= 85:
            return "强烈推荐"
        elif total >= 70:
            return "推荐"
        elif total >= 55:
            return "可以考虑"
        elif total >= 40:
            return "备选"
        else:
            return "不推荐"

    def set_weights(self, weights: DimensionWeights) -> None:
        """设置各维度权重（自动归一化），用于调整评分侧重。"""
        self._weights = weights.normalize()
        self._update_dimension_weights()

    def get_weights(self) -> DimensionWeights:
        """获取当前各维度权重配置。"""
        return self._weights

    def score_batch(
        self, jd: JDParseResult, resumes: list[ResumeParseResult]
    ) -> list[ScoringResult]:
        """批量对多个候选人进行评分，适用于批量招聘场景。"""
        return [self.score(jd, resume) for resume in resumes]
