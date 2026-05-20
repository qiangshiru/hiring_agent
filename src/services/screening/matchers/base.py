from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class MatchResult:
    score: float
    matched: bool
    reason: str | None = None
    confidence: float = 1.0
    details: dict | None = None


class BaseMatcher(ABC):
    @abstractmethod
    def match(self, jd_requirement: str | list[str], resume_value: str | list) -> MatchResult:
        raise NotImplementedError


class ExactMatcher(BaseMatcher):
    def match(self, jd_requirement: str | list[str], resume_value: str | list) -> MatchResult:
        if isinstance(jd_requirement, str):
            jd_requirement = [jd_requirement]
        if isinstance(resume_value, str):
            resume_value = [resume_value]

        jd_set = {v.lower() for v in jd_requirement}
        resume_set = {v.lower() for v in resume_value if v}

        if not jd_set:
            return MatchResult(score=1.0, matched=True, reason="无特定要求")

        matched = jd_set & resume_set
        score = len(matched) / len(jd_set) if jd_set else 1.0

        return MatchResult(
            score=score,
            matched=score >= 1.0,
            reason=f"精确匹配: {len(matched)}/{len(jd_set)}" if matched else "未匹配",
            details={"matched": list(matched), "required": list(jd_set)},
        )


class FuzzyMatcher(BaseMatcher):
    def __init__(self) -> None:
        self._synonyms: dict[str, set[str]] = {
            "python": {"python", "Python", "PYTHON"},
            "java": {"java", "Java", "JAVA"},
            "javascript": {"javascript", "js", "JS"},
            "机器学习": {"ml", "machine learning"},
            "深度学习": {"dl", "deep learning", "深度学习"},
            "ai": {"人工智能", "artificial intelligence"},
        }

    def match(self, jd_requirement: str | list[str], resume_value: str | list) -> MatchResult:
        if isinstance(jd_requirement, str):
            jd_requirement = [jd_requirement]
        if isinstance(resume_value, str):
            resume_value = [resume_value]

        expanded_requirements = self._expand_synonyms(set(jd_requirement))
        resume_set = self._expand_synonyms(set(v.lower() for v in resume_value if v))

        if not expanded_requirements:
            return MatchResult(score=1.0, matched=True, reason="无特定要求")

        matched = expanded_requirements & resume_set
        score = len(matched) / len(expanded_requirements) if expanded_requirements else 1.0

        return MatchResult(
            score=score,
            matched=score >= 0.8,
            reason=f"模糊匹配: {len(matched)}/{len(expanded_requirements)}",
            confidence=0.9,
            details={"matched": list(matched)},
        )

    def _expand_synonyms(self, terms: set[str]) -> set[str]:
        expanded: set[str] = set()
        for term in terms:
            expanded.add(term.lower())
            if term.lower() in self._synonyms:
                expanded.update(self._synonyms[term.lower()])
        return expanded


class SemanticMatcher(BaseMatcher):
    def match(self, jd_requirement: str | list[str], resume_value: str | list) -> MatchResult:
        fuzzy_matcher = FuzzyMatcher()
        result = fuzzy_matcher.match(jd_requirement, resume_value)
        result.confidence = 0.85
        return result
