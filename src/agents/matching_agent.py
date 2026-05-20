from typing import TypedDict

from src.schemas.jd import JDParseResult
from src.schemas.resume import ResumeParseResult
from src.services.scoring import ScoringService
from src.services.screening import ScreeningService


class MatchingState(TypedDict, total=False):
    jd: JDParseResult
    resume: ResumeParseResult
    screening_result: dict | None
    scoring_result: dict | None
    match_reason: str | None


class MatchingAgent:
    def __init__(
        self,
        screening_service: ScreeningService | None = None,
        scoring_service: ScoringService | None = None,
    ) -> None:
        self._screening_service = screening_service or ScreeningService()
        self._scoring_service = scoring_service or ScoringService()

    async def match(
        self, jd: JDParseResult, resume: ResumeParseResult
    ) -> dict:
        screen_result = self._screening_service.screen(jd, resume)
        score_result = self._scoring_service.score(jd, resume)

        match_reason = self._generate_match_reason(screen_result, score_result)

        return {
            "passed": screen_result.passed,
            "screening": {
                "passed": screen_result.passed,
                "reasons": screen_result.reasons,
                "confidence": screen_result.confidence,
            },
            "scoring": {
                "total": score_result.total,
                "dimensions": [
                    {
                        "name": d.name,
                        "score": d.score,
                        "weight": d.weight,
                        "reason": d.reason,
                    }
                    for d in score_result.dimensions
                ],
                "recommendation": score_result.recommendation,
            },
            "match_reason": match_reason,
        }

    def _generate_match_reason(
        self, screen_result, score_result
    ) -> str:
        reasons = []

        if not screen_result.passed:
            reasons.append(f"未通过筛选: {', '.join(screen_result.failed_rules)}")
        else:
            reasons.append("通过硬性条件筛选")

        top_dimensions = sorted(
            score_result.dimensions,
            key=lambda d: d.score,
            reverse=True
        )[:2]
        for dim in top_dimensions:
            if dim.score >= 70:
                reasons.append(f"{dim.name}表现优秀({dim.score:.0f}分)")

        if score_result.total >= 70:
            reasons.append(f"综合评分{score_result.total:.0f}分，{score_result.recommendation}")

        return "；".join(reasons)


def build_matching_agent(
    screening_service: ScreeningService | None = None,
    scoring_service: ScoringService | None = None,
) -> MatchingAgent:
    return MatchingAgent(screening_service, scoring_service)
