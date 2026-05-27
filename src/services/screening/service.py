"""简历初筛服务。

基于 JD 要求和候选人简历执行多维度规则匹配，判断候选人是否满足职位的基本要求。
筛选规则按优先级排序，包含必选规则和可选规则，最终输出通过/失败状态及置信度评分，
支持规则的热添加和移除以及批量筛选。
"""

from typing import Protocol, Optional

from src.core.logging import get_logger
from src.schemas.jd import JDParseResult
from src.schemas.resume import ResumeParseResult
from src.schemas.screening import RuleMatch, ScreeningResult
from src.services.screening.rules import RuleResult, ScreeningRule, create_default_rules

logger = get_logger(__name__)


class ScreeningCache(Protocol):
    """筛选结果缓存协议，定义缓存的读写接口。"""

    async def get(self, key: str) -> Optional[ScreeningResult]:
        raise NotImplementedError

    async def set(self, key: str, value: ScreeningResult, ttl_seconds: int) -> None:
        raise NotImplementedError


class NullScreeningCache:
    """空缓存实现（不使用缓存时回退到此实现）。"""
    async def get(self, key: str) -> Optional[ScreeningResult]:
        return None

    async def set(self, key: str, value: ScreeningResult, ttl_seconds: int) -> None:
        return None


class ScreeningService:
    """简历初筛服务核心类。

    根据 JD 和简历执行多维度规则匹配筛选，规则按优先级降序排列。
    必选规则（required=True）全部通过才算筛选通过，可选规则影响置信度评分。
    """

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
            extra={"candidate_name": resume.姓名 or "unknown", "rules_count": len(self._rules)},
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
                    extra={"rule_id": result.rule_id, "rule_name": result.rule_name, "score": result.score},
                )
            else:
                failed_rules.append(result.rule_name)
                if result.reason:
                    reasons.append(result.reason)
                logger.debug(
                    "rule_failed",
                    extra={"rule_id": result.rule_id, "rule_name": result.rule_name, "reason": result.reason},
                )

        # 所有必选规则均通过才算筛选通过，未匹配到的必选规则视为未通过
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
            extra={
                "candidate_name": resume.姓名 or "unknown",
                "passed": passed,
                "confidence": confidence,
                "matched_rules_count": len(matched_rules),
                "failed_rules_count": len(failed_rules),
            },
        )

        return result

    def _find_rule(self, rule_id: str) -> Optional[ScreeningRule]:
        """根据规则 ID 在规则列表中查找对应的规则对象。"""
        for rule in self._rules:
            if rule.rule_id == rule_id:
                return rule
        return None

    def _calculate_confidence(self, rule_results: list[RuleMatch]) -> float:
        """计算筛选置信度，取所有通过规则的评分的平均值。"""
        if not rule_results:
            return 0.0

        passed_results = [r for r in rule_results if r.passed]
        if not passed_results:
            return 0.0

        total_confidence = sum(r.score for r in passed_results) / len(passed_results)
        return round(total_confidence, 3)

    def add_rule(self, rule: ScreeningRule) -> None:
        """动态添加筛选规则，添加后按优先级重新排序。"""
        self._rules.append(rule)
        self._rules.sort(key=lambda r: r.priority, reverse=True)
        logger.info(
            "rule_added",
            extra={"rule_id": rule.rule_id, "rule_name": rule.rule_name, "priority": rule.priority},
        )

    def remove_rule(self, rule_id: str) -> bool:
        """根据规则 ID 移除筛选规则，返回是否成功移除。"""
        original_len = len(self._rules)
        self._rules = [r for r in self._rules if r.rule_id != rule_id]
        removed = len(self._rules) < original_len
        if removed:
            logger.info("rule_removed", extra={"rule_id": rule_id})
        return removed

    def get_rules(self) -> list[ScreeningRule]:
        """获取当前配置的所有筛选规则列表（副本）。"""
        return list(self._rules)

    def screen_batch(
        self, jd: JDParseResult, resumes: list[ResumeParseResult]
    ) -> list[ScreeningResult]:
        """批量筛选多个候选人简历，适用于大批量招聘场景。"""
        logger.info("screening_batch_start", extra={"resumes_count": len(resumes)})
        results = [self.screen(jd, resume) for resume in resumes]
        logger.info("screening_batch_complete", extra={"resumes_count": len(resumes)})
        return results
