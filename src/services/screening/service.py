from typing import Protocol, Optional

from src.core.logging import get_logger
from src.schemas.jd import JDParseResult
from src.schemas.resume import ResumeParseResult
from src.schemas.screening import RuleMatch, ScreeningResult
from src.services.screening.rules import RuleResult, ScreeningRule, create_default_rules

logger = get_logger(__name__)


class ScreeningCache(Protocol):
    async def get(self, key: str) -> Optional[ScreeningResult]:
        raise NotImplementedError

    async def set(self, key: str, value: ScreeningResult, ttl_seconds: int) -> None:
        raise NotImplementedError


class NullScreeningCache:
    async def get(self, key: str) -> Optional[ScreeningResult]:
        return None

    async def set(self, key: str, value: ScreeningResult, ttl_seconds: int) -> None:
        return None


class ScreeningService:
    def __init__(
        self,
        rules: Optional[list[ScreeningRule]] = None,
        cache: Optional[ScreeningCache] = None,
    ) -> None:
        self._rules = rules or create_default_rules()
        self._cache = cache if cache is not None else NullScreeningCache()
        self._rules.sort(key=lambda r: r.priority, reverse=True)

    def screen(
        self, jd: JDParseResult, resume: ResumeParseResult
    ) -> ScreeningResult:
        """根据 JD 和简历进行筛选评分。
        
        Args:
            jd: 解析后的 JD 结果
            resume: 解析后的简历结果
        
        Returns:
            筛选结果，包含通过/失败状态、置信度和原因
        
        Raises:
            ValueError: JD 或简历为空
        """
        if not jd:
            raise ValueError("JD 不能为空")
        if not resume:
            raise ValueError("简历不能为空")

        logger.info(
            "screening_start",
            candidate_name=resume.姓名 or "unknown",
            rules_count=len(self._rules),
        )

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
                logger.debug(
                    "rule_passed",
                    rule_id=result.rule_id,
                    rule_name=result.rule_name,
                    score=result.score,
                )
            else:
                failed_rules.append(result.rule_name)
                if result.reason:
                    reasons.append(result.reason)
                logger.debug(
                    "rule_failed",
                    rule_id=result.rule_id,
                    rule_name=result.rule_name,
                    reason=result.reason,
                )

        required_rules = [r for r in self._rules if r.required]
        passed = all(
            next(
                (rm for rm in rule_results if rm.rule_id == r.rule_id),
                RuleMatch(rule_id=r.rule_id, rule_name=r.rule_name, passed=False),
            ).passed
            for r in required_rules
        )

        confidence = self._calculate_confidence(rule_results)

        result = ScreeningResult(
            passed=passed,
            reasons=reasons,
            failed_rules=failed_rules,
            matched_rules=matched_rules,
            confidence=confidence,
        )

        logger.info(
            "screening_complete",
            candidate_name=resume.姓名 or "unknown",
            passed=passed,
            confidence=confidence,
            matched_rules_count=len(matched_rules),
            failed_rules_count=len(failed_rules),
        )

        return result

    def _find_rule(self, rule_id: str) -> Optional[ScreeningRule]:
        """根据规则ID查找规则。"""
        for rule in self._rules:
            if rule.rule_id == rule_id:
                return rule
        return None

    def _calculate_confidence(self, rule_results: list[RuleMatch]) -> float:
        """计算筛选置信度。"""
        if not rule_results:
            return 0.0

        passed_results = [r for r in rule_results if r.passed]
        if not passed_results:
            return 0.0

        total_confidence = sum(r.score for r in passed_results) / len(passed_results)
        return round(total_confidence, 3)

    def add_rule(self, rule: ScreeningRule) -> None:
        """添加筛选规则。"""
        self._rules.append(rule)
        self._rules.sort(key=lambda r: r.priority, reverse=True)
        logger.info(
            "rule_added",
            rule_id=rule.rule_id,
            rule_name=rule.rule_name,
            priority=rule.priority,
        )

    def remove_rule(self, rule_id: str) -> bool:
        """移除筛选规则。"""
        original_len = len(self._rules)
        self._rules = [r for r in self._rules if r.rule_id != rule_id]
        removed = len(self._rules) < original_len
        if removed:
            logger.info("rule_removed", extra={"rule_id": rule_id})
        return removed

    def get_rules(self) -> list[ScreeningRule]:
        """获取所有筛选规则。"""
        return list(self._rules)

    def screen_batch(
        self, jd: JDParseResult, resumes: list[ResumeParseResult]
    ) -> list[ScreeningResult]:
        """批量筛选多个简历。"""
        logger.info("screening_batch_start", extra={"resumes_count": len(resumes)})
        results = [self.screen(jd, resume) for resume in resumes]
        logger.info("screening_batch_complete", extra={"resumes_count": len(resumes)})
        return results
