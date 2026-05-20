import re
from abc import ABC, abstractmethod
from collections.abc import Sequence

from pydantic import BaseModel

from src.config import Settings
from src.schemas.jd import EducationRequirement, SalaryRange, TechStackRequirement, WorkExperienceRequirement


class ExtractorError(Exception):
    """Raised when a JD field extractor fails."""


class ExtractionContext(BaseModel):
    text: str
    settings: Settings


class BaseExtractor[T](ABC):
    @abstractmethod
    def extract(self, context: ExtractionContext) -> T:
        raise NotImplementedError


def _unique_preserve_order(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = value.strip()
        if normalized and normalized.lower() not in seen:
            seen.add(normalized.lower())
            result.append(normalized)
    return result


class EducationExtractor(BaseExtractor[EducationRequirement]):
    def extract(self, context: ExtractionContext) -> EducationRequirement:
        text = context.text
        must: list[str] = []
        bonus: list[str] = []

        for term in context.settings.jd_parser_education_terms:
            if term not in text:
                continue
            window = _nearby_text(text, term)
            if term == "985" and "985优先" in text:
                must.append(term)
            elif _contains_any(window, context.settings.jd_parser_bonus_hints) or "优先" in window:
                bonus.append(term)
            else:
                must.append(term)

        if "985" in text and "211" not in text and "985优先" in text:
            bonus.append("211")

        return EducationRequirement(must=_unique_preserve_order(must), bonus=_unique_preserve_order(bonus))


class WorkExperienceExtractor(BaseExtractor[WorkExperienceRequirement]):
    def extract(self, context: ExtractionContext) -> WorkExperienceRequirement:
        text = context.text
        min_years: int | None = None
        max_years: int | None = None

        range_match = re.search(r"(?P<min>\d+)\s*[-~到至]\s*(?P<max>\d+)\s*年", text)
        if range_match is not None:
            min_years = int(range_match.group("min"))
            max_years = int(range_match.group("max"))
            return WorkExperienceRequirement(min_years=min_years, max_years=max_years)

        minimum_patterns = [
            r"(?P<years>\d+)\s*年(?:以上|\+)",
            r"(?:至少|不少于|不低于)\s*(?P<years>\d+)\s*年",
            r"(?P<years>\d+)\s*\+\s*years?",
            r"(?P<years>\d+)\s*years?\s*(?:or more|\+)",
        ]
        for pattern in minimum_patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match is not None:
                min_years = int(match.group("years"))
                break

        return WorkExperienceRequirement(min_years=min_years, max_years=max_years)


class TechStackExtractor(BaseExtractor[TechStackRequirement]):
    def extract(self, context: ExtractionContext) -> TechStackRequirement:
        text = context.text
        must: list[str] = []
        bonus: list[str] = []

        for tech in context.settings.jd_parser_known_tech_stacks:
            if re.search(rf"(?<![A-Za-z0-9]){re.escape(tech)}(?![A-Za-z0-9])", text, re.IGNORECASE):
                window = _nearby_text(text, tech)
                if _contains_any(window, context.settings.jd_parser_bonus_hints):
                    bonus.append(tech)
                else:
                    must.append(tech)

        if "熟悉" in text and re.search(r"(?<![A-Za-z0-9])Agent(?![A-Za-z0-9])", text, re.IGNORECASE):
            must = [tech for tech in must if tech.lower() != "agent"]
            bonus.append("Agent")

        return TechStackRequirement(
            must=_unique_preserve_order(must),
            bonus=_unique_preserve_order(bonus),
        )


class IndustryExperienceExtractor(BaseExtractor[list[str]]):
    def extract(self, context: ExtractionContext) -> list[str]:
        patterns = [
            r"(?P<industry>[\u4e00-\u9fa5A-Za-z0-9]+)(?:行业|领域)(?:经验|背景)",
            r"(?:有|具备)(?P<industry>[\u4e00-\u9fa5A-Za-z0-9]+)(?:行业|领域)",
        ]
        matches: list[str] = []
        for pattern in patterns:
            matches.extend(match.group("industry") for match in re.finditer(pattern, context.text))
        return _unique_preserve_order(matches)


class CityExtractor(BaseExtractor[list[str]]):
    def extract(self, context: ExtractionContext) -> list[str]:
        return _unique_preserve_order(
            [city for city in context.settings.jd_parser_city_terms if city in context.text]
        )


class SalaryExtractor(BaseExtractor[SalaryRange | None]):
    def extract(self, context: ExtractionContext) -> SalaryRange | None:
        text = context.text
        monthly_range = re.search(
            r"(?P<min>\d+(?:\.\d+)?)\s*[kK]\s*[-~到至]\s*(?P<max>\d+(?:\.\d+)?)\s*[kK]",
            text,
        )
        if monthly_range is not None:
            min_salary = int(float(monthly_range.group("min")) * 1000)
            max_salary = int(float(monthly_range.group("max")) * 1000)
            return SalaryRange(
                min_monthly=min_salary,
                max_monthly=max_salary,
                raw=monthly_range.group(0),
            )

        chinese_range = re.search(
            r"(?P<min>\d+(?:\.\d+)?)\s*万\s*[-~到至]\s*(?P<max>\d+(?:\.\d+)?)\s*万",
            text,
        )
        if chinese_range is not None:
            min_salary = int(float(chinese_range.group("min")) * 10000 / 12)
            max_salary = int(float(chinese_range.group("max")) * 10000 / 12)
            return SalaryRange(
                min_monthly=min_salary,
                max_monthly=max_salary,
                raw=chinese_range.group(0),
            )
        return None


def default_extractors() -> dict[str, BaseExtractor[object]]:
    return {
        "education": EducationExtractor(),
        "work_experience": WorkExperienceExtractor(),
        "tech_stack": TechStackExtractor(),
        "industry_experience": IndustryExperienceExtractor(),
        "city": CityExtractor(),
        "salary": SalaryExtractor(),
    }


def _contains_any(text: str, hints: Sequence[str]) -> bool:
    lowered_text = text.lower()
    return any(hint.lower() in lowered_text for hint in hints)


def _nearby_text(text: str, keyword: str, radius: int = 12) -> str:
    index = text.lower().find(keyword.lower())
    if index < 0:
        return ""
    return text[max(0, index - radius) : index + len(keyword) + radius]
