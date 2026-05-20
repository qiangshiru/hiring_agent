import re
from typing import Optional

from src.schemas.resume import Skill
from src.services.resume_parser.extractors.base import (
    BaseExtractor,
    RuleBasedExtractor,
)


class SkillsExtractor(RuleBasedExtractor[list[Skill]]):
    skill_categories = {
        "编程语言": [
            "Python", "Java", "JavaScript", "TypeScript", "Go", "Rust", "C++", "C#",
            "PHP", "Ruby", "Swift", "Kotlin", "Scala", "R", "MATLAB", "Shell", "Bash",
        ],
        "前端技术": [
            "HTML", "CSS", "React", "Vue", "Angular", "Next.js", "Nuxt.js",
            "Tailwind CSS", "Bootstrap", "jQuery", "Webpack", "Vite",
        ],
        "后端技术": [
            "Django", "Flask", "FastAPI", "Spring", "Spring Boot", "Node.js",
            "Express", "NestJS", "Rails", "Laravel", "Gin", "Echo",
        ],
        "数据库": [
            "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch",
            "Cassandra", "DynamoDB", "SQLite", "Oracle", "SQL Server",
        ],
        "大数据": [
            "Hadoop", "Spark", "Hive", "Flink", "Kafka", "Storm",
            "HBase", "Presto", "Impala", "Airflow",
        ],
        "AI/ML": [
            "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "Pandas", "NumPy",
            "OpenCV", "NLTK", "SpaCy", "LangChain", "RAG", "Agent",
        ],
        "DevOps": [
            "Docker", "Kubernetes", "Jenkins", "GitLab CI", "GitHub Actions",
            "Ansible", "Terraform", "Prometheus", "Grafana", "ELK",
        ],
        "云服务": [
            "AWS", "Azure", "GCP", "阿里云", "腾讯云", "华为云",
            "EC2", "S3", "Lambda", "ECS", "EKS", "CloudFormation",
        ],
    }

    proficiency_keywords = {
        "精通": ["精通", "专家", "熟练精通"],
        "熟练": ["熟练", "熟练掌握"],
        "熟悉": ["熟悉", "掌握", "了解"],
        "了解": ["了解", "初学", "入门"],
    }

    def extract(self, text: str) -> list[Skill]:
        skills: list[Skill] = []
        found_skills: set[str] = set()

        for category, techs in self.skill_categories.items():
            for tech in techs:
                if tech.lower() in text.lower():
                    proficiency = self._extract_proficiency(text, tech)
                    skill_obj = Skill(
                        名称=tech,
                        类别=category,
                        熟练度=proficiency,
                        置信度=self._calculate_confidence(text, tech),
                    )
                    key = tech.lower()
                    if key not in found_skills:
                        skills.append(skill_obj)
                        found_skills.add(key)

        skills = self._merge_similar_skills(skills)
        return skills

    def _extract_proficiency(self, text: str, skill: str) -> Optional[str]:
        context = self._get_context_around(text, skill)
        if not context:
            return None

        for proficiency, keywords in self.proficiency_keywords.items():
            if any(kw in context for kw in keywords):
                return proficiency

        if f"精通{skill}" in text or f"熟练{skill}" in text:
            return "熟练"
        if f"熟悉{skill}" in text:
            return "熟悉"

        return None

    def _get_context_around(self, text: str, skill: str, radius: int = 15) -> str:
        index = text.lower().find(skill.lower())
        if index < 0:
            return ""
        start = max(0, index - radius)
        end = min(len(text), index + len(skill) + radius)
        return text[start:end]

    def _calculate_confidence(self, text: str, skill: str) -> float:
        skill_lower = skill.lower()
        text_lower = text.lower()

        if skill_lower not in text_lower:
            return 0.0

        base_confidence = 0.6

        skill_count = text_lower.count(skill_lower)
        if skill_count > 3:
            base_confidence += 0.2
        elif skill_count > 1:
            base_confidence += 0.1

        context = self._get_context_around(text, skill)
        if context:
            if any(kw in context for kw in ["精通", "熟练", "掌握"]):
                base_confidence += 0.15
            elif "熟悉" in context:
                base_confidence += 0.1

        skill_mentions = len(re.findall(rf"\b{re.escape(skill)}\b", text, re.IGNORECASE))
        if skill_mentions > 5:
            base_confidence += 0.1

        return min(1.0, base_confidence)

    def _merge_similar_skills(self, skills: list[Skill]) -> list[Skill]:
        merged: dict[str, Skill] = {}
        for skill in skills:
            key = skill.名称.lower()
            if key in merged:
                existing = merged[key]
                if skill.置信度 > existing.置信度:
                    merged[key] = skill
                elif not existing.熟练度 and skill.熟练度:
                    existing.熟练度 = skill.熟练度
            else:
                merged[key] = skill

        result = list(merged.values())
        result.sort(key=lambda x: (-x.置信度, x.类别 or ""))
        return result

    def extract_from_sections(self, text: str) -> list[Skill]:
        skills: list[Skill] = []
        found_skills: set[str] = set()

        section_patterns = [
            r"(?:技能|专业技能|技术栈|技术能力)(.*?)(?:\n\n|\Z)",
            r"(?:掌握|熟悉)(.*?)(?:\n\n|\Z)",
        ]

        for pattern in section_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                section_text = match.group(1)
                section_skills = self.extract(section_text)
                for skill in section_skills:
                    key = skill.名称.lower()
                    if key not in found_skills:
                        skills.append(skill)
                        found_skills.add(key)

        return skills if skills else self.extract(text)
