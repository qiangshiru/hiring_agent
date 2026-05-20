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
    async def get(self, key: str) -> ScoringResult | None:
        raise NotImplementedError

    async def set(self, key: str, value: ScoringResult, ttl_seconds: int) -> None:
        raise NotImplementedError


class NullScoringCache:
    async def get(self, key: str) -> ScoringResult | None:
        return None

    async def set(self, key: str, value: ScoringResult, ttl_seconds: int) -> None:
        return None


class ScoringService:
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
        sorted_dims = sorted(dimensions, key=lambda d: d.score, reverse=True)
        top = sorted_dims[0]
        bottom = sorted_dims[-1]

        return (
            f"总分: {total:.0f}分 | "
            f"最高: {top.name}({top.score:.0f}) | "
            f"最低: {bottom.name}({bottom.score:.0f})"
        )

    def _generate_recommendation(self, total: float) -> str:
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
        self._weights = weights.normalize()
        self._update_dimension_weights()

    def get_weights(self) -> DimensionWeights:
        return self._weights

    def score_batch(
        self, jd: JDParseResult, resumes: list[ResumeParseResult]
    ) -> list[ScoringResult]:
        return [self.score(jd, resume) for resume in resumes]
