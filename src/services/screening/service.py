from typing import Protocol

from src.schemas.jd import JDParseResult
from src.schemas.resume import ResumeParseResult
from src.schemas.screening import RuleMatch, ScreeningResult
from src.services.screening.rules import RuleResult, ScreeningRule, create_default_rules


class ScreeningCache(Protocol):
    async def get(self, key: str) -> ScreeningResult | None:
        raise NotImplementedError

    async def set(self, key: str, value: ScreeningResult, ttl_seconds: int) -> None:
        raise NotImplementedError


class NullScreeningCache:
    async def get(self, key: str) -> ScreeningResult | None:
        return None

    async def set(self, key: str, value: ScreeningResult, ttl_seconds: int) -> None:
        return None


class ScreeningService:
    def __init__(
        self,
        rules: list[ScreeningRule] | None = None,
        cache: ScreeningCache | None = None,
    ) -> None:
        self._rules = rules or create_default_rules()
        self._cache = cache if cache is not None else NullScreeningCache()
        self._rules.sort(key=lambda r: r.priority, reverse=True)

    def screen(
        self, jd: JDParseResult, resume: ResumeParseResult
    ) -> ScreeningResult:
        rule_results: list[RuleMatch] = []
        failed_rules: list[str] = []
        matched_rules: list[str] = []
        reasons: list[str] = []

        for rule in self._rules:
            result = rule.evaluate(jd, resume)
            rule_match = RuleMatch(
                rule_id=result.rule_id,
                rule_name=result.rule_name,
                passed=result.passed,
                score=result.score,
                reason=result.reason,
            )
            rule_results.append(rule_match)

            if result.passed:
                matched_rules.append(result.rule_name)
            else:
                failed_rules.append(result.rule_name)
                if result.reason:
                    reasons.append(result.reason)

        passed = all(r.passed or not self._rules[self._rules.index(rule := self._find_rule(r.rule_id))].required
                     for r in rule_results)

        required_rules = [r for r in self._rules if r.required]
        passed = all(
            next((rm for rm in rule_results if rm.rule_id == r.rule_id), RuleMatch(rule_id=r.rule_id, rule_name=r.rule_name, passed=False)).passed
            for r in required_rules
        )

        confidence = self._calculate_confidence(rule_results)

        return ScreeningResult(
            passed=passed,
            reasons=reasons,
            failed_rules=failed_rules,
            matched_rules=matched_rules,
            confidence=confidence,
        )

    def _find_rule(self, rule_id: str) -> ScreeningRule | None:
        for rule in self._rules:
            if rule.rule_id == rule_id:
                return rule
        return None

    def _calculate_confidence(self, rule_results: list[RuleMatch]) -> float:
        if not rule_results:
            return 0.0

        total_confidence = sum(
            r.score for r in rule_results if r.passed
        ) / len(rule_results)
        return round(total_confidence, 3)

    def add_rule(self, rule: ScreeningRule) -> None:
        self._rules.append(rule)
        self._rules.sort(key=lambda r: r.priority, reverse=True)

    def remove_rule(self, rule_id: str) -> bool:
        original_len = len(self._rules)
        self._rules = [r for r in self._rules if r.rule_id != rule_id]
        return len(self._rules) < original_len

    def get_rules(self) -> list[ScreeningRule]:
        return list(self._rules)

    def screen_batch(
        self, jd: JDParseResult, resumes: list[ResumeParseResult]
    ) -> list[ScreeningResult]:
        return [self.screen(jd, resume) for resume in resumes]
