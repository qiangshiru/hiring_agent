import re
from datetime import datetime
from typing import Annotated

from src.schemas.resume import Education
from src.services.resume_parser.extractors.base import (
    BaseExtractor,
    RuleBasedExtractor,
)


class EducationExtractor(RuleBasedExtractor[list[Education]]):
    education_keywords = ["大学", "学院", "学校", "硕士", "本科", "博士", "大专", "高中"]
    degree_keywords = ["博士", "硕士", "本科", "大专", "学士", "高中", "MBA", "EMBA"]

    def extract(self, text: str) -> list[Education]:
        educations: list[Education] = []
        blocks = self._split_into_blocks(text)

        for block in blocks:
            if self._is_education_block(block):
                education = self._parse_education_block(block)
                if education:
                    educations.append(education)

        return self._merge_duplicate_educations(educations)

    def _split_into_blocks(self, text: str) -> list[str]:
        lines = text.split("\n")
        blocks: list[str] = []
        current_block: list[str] = []

        for line in lines:
            stripped = line.strip()
            if stripped:
                current_block.append(stripped)
            elif current_block:
                blocks.append("\n".join(current_block))
                current_block = []

        if current_block:
            blocks.append("\n".join(current_block))

        return blocks

    def _is_education_block(self, block: str) -> bool:
        block_lower = block.lower()
        return any(keyword in block for keyword in self.education_keywords)

    def _parse_education_block(self, block: str) -> Education | None:
        school = self._extract_school(block)
        degree = self._extract_degree(block)
        major = self._extract_major(block)
        start_date, end_date = self._extract_dates(block)

        if not school and not degree:
            return None

        confidence = self._calculate_block_confidence(block, school, degree)
        return Education(
            学校=school,
            学历=degree,
            专业=major,
            开始时间=start_date,
            结束时间=end_date,
            描述=block if len(block) < 500 else block[:500],
            置信度=confidence,
        )

    def _extract_school(self, block: str) -> str | None:
        patterns = [
            r"(?:毕业于|就读于|肄业于)\s*([^\n,，,]+(?:大学|学院|学校))",
            r"([^\n,，]+(?:大学|学院|学校))\s*(?:.{0,10}(?:本科|硕士|博士|在读))?",
            r"([^\n,，]+(?:大学|学院))\s*-\s*(?:.{0,10}(?:本科|硕士|博士|在读))?",
        ]

        for pattern in patterns:
            match = re.search(pattern, block)
            if match:
                school = match.group(1).strip()
                if len(school) >= 2:
                    return school
        return None

    def _extract_degree(self, block: str) -> str | None:
        degree_pattern = "|".join(self.degree_keywords)
        pattern = rf"({degree_pattern})(?:学位|学历)?"
        match = re.search(pattern, block)
        if match:
            return match.group(1)
        return None

    def _extract_major(self, block: str) -> str | None:
        patterns = [
            r"(?:专业|主修)\s*[:：]?\s*([^\n,，]+)",
            r"([\u4e00-\u9fa5]{2,20}?(?:学|工程|科学|技术|经济|管理|文学|艺术|教育))",
        ]

        for pattern in patterns:
            match = re.search(pattern, block)
            if match:
                major = match.group(1).strip()
                if major and major not in self.degree_keywords:
                    return major
        return None

    def _extract_dates(self, block: str) -> tuple[datetime | None, datetime | None]:
        date_pattern = r"(\d{4})\s*[-~至]\s*(\d{4}|\d{2}|(?:至今|现在))"
        match = re.search(date_pattern, block)
        if match:
            start_year = int(match.group(1))
            end_str = match.group(2)
            end_year = datetime.now().year if end_str in ["至今", "现在"] else int(end_str)

            start = datetime(start_year, 9, 1)
            end = datetime(end_year, 6, 30) if end_year != datetime.now().year else None
            return start, end
        return None, None

    def _calculate_block_confidence(self, block: str, school: str | None, degree: str | None) -> float:
        confidence = 0.5
        if school:
            confidence += 0.3
        if degree:
            confidence += 0.2
        if re.search(r"\d{4}", block):
            confidence += 0.1
        return min(1.0, confidence)

    def _merge_duplicate_educations(self, educations: list[Education]) -> list[Education]:
        if not educations:
            return []
        seen: dict[str, Education] = {}
        for edu in sorted(educations, key=lambda x: x.开始时间 or datetime.min, reverse=True):
            key = (edu.学校 or "") + (edu.学历 or "")
            if key not in seen:
                seen[key] = edu
        return list(seen.values())
