from src.schemas.jd import JDParseResult
from src.schemas.resume import ResumeParseResult
from src.services.scoring.dimensions.base import BaseDimensionScorer, DimensionResult
from src.services.screening.matchers import TechStackMatcher


class TechMatchScorer(BaseDimensionScorer):
    def __init__(self) -> None:
        super().__init__("tech_match", "技术栈匹配度", weight=0.25)
        self._matcher = TechStackMatcher()

    def score(self, jd: JDParseResult, resume: ResumeParseResult) -> DimensionResult:
        jd_must_techs = jd.技术栈.must
        jd_bonus_techs = jd.技术栈.bonus
        resume_skills = [s.名称 for s in resume.技能]

        if not jd_must_techs and not jd_bonus_techs:
            return DimensionResult(
                score=50.0,
                reason="JD无技术栈要求",
                confidence=0.8,
            )

        must_match = self._matcher.match(jd_must_techs, resume_skills)
        bonus_match = self._matcher.match(jd_bonus_techs, resume_skills)

        must_score = must_match.score * 100
        bonus_score = bonus_match.score * 30

        total_score = self._clamp_score(must_score + bonus_score)

        matched_count = 0
        if must_match.details:
            matched_count = len(must_match.details.get("matched", []))
        missing_count = len(jd_must_techs) - matched_count

        if missing_count > 0:
            reason = f"技术栈匹配: 必需项 {matched_count}/{len(jd_must_techs)}, 缺失: {missing_count}"
        else:
            reason = f"技术栈完全匹配: 必需项 {matched_count}/{len(jd_must_techs)}"

        return DimensionResult(
            score=total_score,
            reason=reason,
            confidence=self._calculate_confidence(jd, resume),
            details={
                "must_score": must_score,
                "bonus_score": bonus_score,
                "matched_techs": matched_count,
                "required_techs": len(jd_must_techs),
            },
        )
