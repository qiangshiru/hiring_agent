from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from src.schemas.jd import JDParseResult
from src.schemas.resume import ResumeParseResult


class RuleType(Enum):
    EDUCATION = "education"
    WORK_EXPERIENCE = "work_experience"
    TECH_STACK = "tech_stack"
    CITY = "city"
    SALARY = "salary"
    COMPOSITE = "composite"


class LogicOperator(Enum):
    AND = "and"
    OR = "or"


@dataclass
class RuleResult:
    rule_id: str
    rule_name: str
    passed: bool
    score: float = 0.0
    reason: str | None = None
    details: dict[str, Any] = field(default_factory=dict)


class ScreeningRule(ABC):
    def __init__(
        self,
        rule_id: str,
        rule_name: str,
        rule_type: RuleType,
        priority: int = 0,
        required: bool = True,
    ) -> None:
        self.rule_id = rule_id
        self.rule_name = rule_name
        self.rule_type = rule_type
        self.priority = priority
        self.required = required

    @abstractmethod
    def evaluate(
        self, jd: JDParseResult, resume: ResumeParseResult
    ) -> RuleResult:
        raise NotImplementedError


class EducationRule(ScreeningRule):
    def __init__(
        self,
        rule_id: str,
        rule_name: str,
        required_degrees: list[str] | None = None,
        preferred_degrees: list[str] | None = None,
        priority: int = 0,
        required: bool = True,
    ) -> None:
        super().__init__(rule_id, rule_name, RuleType.EDUCATION, priority, required)
        self.required_degrees = required_degrees or []
        self.preferred_degrees = preferred_degrees or []

    def evaluate(self, jd: JDParseResult, resume: ResumeParseResult) -> RuleResult:
        if not resume.教育:
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=not self.required,
                score=0.0,
                reason="无教育背景信息" if self.required else None,
            )

        resume_degrees = [e.学历 for e in resume.教育 if e.学历]
        required_passed = not self.required_degrees or any(
            deg in resume_degrees for deg in self.required_degrees
        )
        preferred_matches = sum(1 for deg in resume_degrees if deg in self.preferred_degrees)
        bonus_score = min(1.0, preferred_matches * 0.3)

        if required_passed:
            score = 0.5 + bonus_score
            reason = f"学历符合要求"
        else:
            score = 0.0
            reason = f"学历不符合要求，需要: {self.required_degrees}"

        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=required_passed if self.required else True,
            score=score,
            reason=reason,
            details={"resume_degrees": resume_degrees},
        )


class WorkExperienceRule(ScreeningRule):
    def __init__(
        self,
        rule_id: str,
        rule_name: str,
        min_years: int = 0,
        priority: int = 0,
        required: bool = True,
    ) -> None:
        super().__init__(rule_id, rule_name, RuleType.WORK_EXPERIENCE, priority, required)
        self.min_years = min_years

    def evaluate(self, jd: JDParseResult, resume: ResumeParseResult) -> RuleResult:
        jd_min_years = jd.工作经验.min_years or 0
        required_years = max(self.min_years, jd_min_years)

        total_years = 0
        if resume.工作经验:
            from datetime import datetime

            for exp in resume.工作经验:
                if exp.开始时间:
                    end_time = exp.结束时间 or datetime.now()
                    years = (end_time - exp.开始时间).days / 365
                    total_years += years

        passed = total_years >= required_years
        if passed:
            score = min(1.0, total_years / max(required_years, 3))
            reason = f"工作经验 {total_years:.1f} 年，符合要求"
        else:
            score = total_years / required_years if required_years > 0 else 0.0
            reason = f"工作经验 {total_years:.1f} 年，不满足 {required_years} 年要求"

        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=passed if self.required else True,
            score=score,
            reason=reason,
            details={"total_years": round(total_years, 1), "required_years": required_years},
        )


class TechStackRule(ScreeningRule):
    def __init__(
        self,
        rule_id: str,
        rule_name: str,
        required_techs: list[str] | None = None,
        preferred_techs: list[str] | None = None,
        priority: int = 0,
        required: bool = True,
    ) -> None:
        super().__init__(rule_id, rule_name, RuleType.TECH_STACK, priority, required)
        self.required_techs = required_techs or []
        self.preferred_techs = preferred_techs or []

    def evaluate(self, jd: JDParseResult, resume: ResumeParseResult) -> RuleResult:
        resume_skills = {s.名称.lower() for s in resume.技能}
        resume_techs: set[str] = set()
        if resume.项目:
            for proj in resume.项目:
                if proj.技术栈:
                    resume_techs.update(t.lower() for t in proj.技术栈)

        jd_required = {t.lower() for t in jd.技术栈.must}
        jd_bonus = {t.lower() for t in jd.技术栈.bonus}
        all_jd_techs = jd_required | jd_bonus

        required_set = set(self.required_techs) | jd_required
        preferred_set = set(self.preferred_techs) | jd_bonus

        missing_required = required_set - resume_skills - resume_techs
        matched_preferred = preferred_set & (resume_skills | resume_techs)

        required_passed = len(missing_required) == 0
        match_rate = len(matched_preferred) / len(preferred_set) if preferred_set else 1.0

        if required_passed:
            score = 0.6 + match_rate * 0.4
            reason = f"技术栈匹配，必需项全部满足，偏好匹配率 {match_rate:.0%}"
        else:
            score = len(required_set - missing_required) / len(required_set)
            reason = f"缺少必需技术: {', '.join(missing_required)}"

        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=required_passed if self.required else True,
            score=score,
            reason=reason,
            details={
                "matched_preferred": list(matched_preferred),
                "missing_required": list(missing_required),
            },
        )


class CityRule(ScreeningRule):
    def __init__(
        self,
        rule_id: str,
        rule_name: str,
        required_cities: list[str] | None = None,
        priority: int = 0,
        required: bool = False,
    ) -> None:
        super().__init__(rule_id, rule_name, RuleType.CITY, priority, required)
        self.required_cities = required_cities or []

    def evaluate(self, jd: JDParseResult, resume: ResumeParseResult) -> RuleResult:
        jd_cities = {c for c in jd.城市要求}
        required_cities = set(self.required_cities) | jd_cities

        if not required_cities:
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=True,
                score=1.0,
                reason="无城市要求",
            )

        resume_city = resume.城市 or ""
        matched = resume_city in required_cities

        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=matched if self.required else True,
            score=1.0 if matched else 0.0,
            reason=f"城市匹配: {resume_city}" if matched else f"期望城市: {resume_city}",
            details={"resume_city": resume_city, "required_cities": list(required_cities)},
        )


class SalaryRule(ScreeningRule):
    def __init__(
        self,
        rule_id: str,
        rule_name: str,
        priority: int = 0,
        required: bool = False,
    ) -> None:
        super().__init__(rule_id, rule_name, RuleType.SALARY, priority, required)

    def evaluate(self, jd: JDParseResult, resume: ResumeParseResult) -> RuleResult:
        if not jd.薪资范围 or not jd.薪资范围.min_monthly:
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                passed=True,
                score=1.0,
                reason="JD未指定薪资范围",
            )

        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=True,
            score=1.0,
            reason=f"薪资范围: {jd.薪资范围.min_monthly}-{jd.薪资范围.max_monthly}",
            details={"salary_range": f"{jd.薪资范围.min_monthly}-{jd.薪资范围.max_monthly}"},
        )


class CompositeRule(ScreeningRule):
    def __init__(
        self,
        rule_id: str,
        rule_name: str,
        sub_rules: list[ScreeningRule],
        operator: LogicOperator = LogicOperator.AND,
        priority: int = 0,
        required: bool = True,
    ) -> None:
        super().__init__(rule_id, rule_name, RuleType.COMPOSITE, priority, required)
        self.sub_rules = sub_rules
        self.operator = operator

    def evaluate(self, jd: JDParseResult, resume: ResumeParseResult) -> RuleResult:
        results = [rule.evaluate(jd, resume) for rule in self.sub_rules]

        if self.operator == LogicOperator.AND:
            passed = all(r.passed for r in results)
            score = sum(r.score for r in results) / len(results)
        else:
            passed = any(r.passed for r in results)
            score = max(r.score for r in results) if results else 0.0

        sub_results = {r.rule_id: r.passed for r in results}

        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=passed if self.required else True,
            score=score,
            reason=f"组合规则({self.operator.value}): {'通过' if passed else '未通过'}",
            details={"sub_rules": sub_results},
        )


def create_default_rules() -> list[ScreeningRule]:
    return [
        EducationRule(
            rule_id="edu_required",
            rule_name="学历要求",
            required_degrees=["本科"],
            preferred_degrees=["985", "211", "硕士", "博士"],
            priority=10,
            required=True,
        ),
        WorkExperienceRule(
            rule_id="work_exp_required",
            rule_name="工作经验要求",
            min_years=0,
            priority=9,
            required=True,
        ),
        TechStackRule(
            rule_id="tech_required",
            rule_name="技术栈要求",
            priority=8,
            required=True,
        ),
        CityRule(
            rule_id="city_preferred",
            rule_name="城市偏好",
            priority=5,
            required=False,
        ),
        SalaryRule(
            rule_id="salary_check",
            rule_name="薪资范围检查",
            priority=3,
            required=False,
        ),
    ]
