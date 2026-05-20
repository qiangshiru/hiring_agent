from src.services.screening.matchers.base import BaseMatcher, ExactMatcher, MatchResult


class EducationMatcher(BaseMatcher):
    def __init__(self) -> None:
        self._degree_levels = {
            "博士": 5,
            "硕士": 4,
            "MBA": 4,
            "EMBA": 4,
            "本科": 3,
            "一本": 3,
            "二本": 2,
            "大专": 1,
            "高职": 1,
        }

        self._school_tiers = {
            "985": 3,
            "211": 2,
            "一本": 2,
            "清华": 3,
            "北大": 3,
            "复旦": 3,
            "上交": 3,
            "浙大": 3,
            "中科大": 3,
        }

    def match(self, jd_requirement: str | list[str], resume_value: str | list) -> MatchResult:
        if isinstance(jd_requirement, str):
            jd_requirement = [jd_requirement]
        if isinstance(resume_value, str):
            resume_value = [resume_value]

        resume_degrees = [v for v in resume_value if v]
        if not resume_degrees:
            return MatchResult(
                score=0.0,
                matched=False,
                reason="简历中无学历信息",
                confidence=1.0,
            )

        resume_degree_levels = [self._degree_levels.get(d, 0) for d in resume_degrees]
        max_resume_level = max(resume_degree_levels) if resume_degree_levels else 0

        required_levels = [self._degree_levels.get(r, 0) for r in jd_requirement]
        min_required_level = min(required_levels) if required_levels else 0

        matched = max_resume_level >= min_required_level
        score = min(1.0, max_resume_level / max(min_required_level, 1)) if min_required_level else 1.0

        if matched:
            reason = f"学历匹配: {resume_degrees[0]}"
        else:
            reason = f"学历不满足: 需要 {jd_requirement}, 实际 {resume_degrees}"

        return MatchResult(
            score=score,
            matched=matched,
            reason=reason,
            confidence=0.95,
            details={
                "max_resume_level": max_resume_level,
                "min_required_level": min_required_level,
            },
        )

    def match_school_tier(self, jd_tiers: list[str], resume_schools: list[str]) -> MatchResult:
        if not jd_tiers:
            return MatchResult(score=1.0, matched=True, reason="无学校层次要求")

        resume_school_lower = [s.lower() for s in resume_schools]
        matched_tiers = []

        for tier in jd_tiers:
            tier_lower = tier.lower()
            for school in resume_school_lower:
                if tier_lower in school or school in tier_lower:
                    matched_tiers.append(tier)
                    break

        score = len(matched_tiers) / len(jd_tiers) if jd_tiers else 1.0

        return MatchResult(
            score=score,
            matched=score >= 0.5,
            reason=f"学校层次匹配: {len(matched_tiers)}/{len(jd_tiers)}",
            confidence=0.9,
            details={"matched_tiers": matched_tiers},
        )
