from src.services.screening.matchers.base import BaseMatcher, MatchResult


class TechStackMatcher(BaseMatcher):
    def __init__(self) -> None:
        self._tech_synonyms: dict[str, set[str]] = {
            "python": {"python", "Python", "py"},
            "java": {"java", "Java", "JAVA"},
            "javascript": {"javascript", "js", "JS", "ECMAScript"},
            "typescript": {"typescript", "ts", "TS"},
            "golang": {"golang", "go", "Go"},
            "rust": {"rust", "Rust"},
            "c++": {"c++", "cpp", "C++", "CPlusPlus"},
            "c#": {"c#", "csharp", "C#"},
            "vue": {"vue", "vue.js", "Vue"},
            "react": {"react", "react.js", "React", "ReactJS"},
            "angular": {"angular", "angular.js", "Angular"},
            "django": {"django", "Django"},
            "flask": {"flask", "Flask"},
            "fastapi": {"fastapi", "FastAPI"},
            "spring": {"spring", "Spring", "spring boot", "SpringBoot"},
            "mysql": {"mysql", "MySQL"},
            "postgresql": {"postgresql", "postgres", "pg"},
            "mongodb": {"mongodb", "mongo", "MongoDB"},
            "redis": {"redis", "Redis"},
            "kafka": {"kafka", "Kafka"},
            "docker": {"docker", "Docker"},
            "kubernetes": {"kubernetes", "k8s", "K8S"},
            "tensorflow": {"tensorflow", "tf", "TensorFlow"},
            "pytorch": {"pytorch", "torch", "PyTorch"},
            "pytorch": {"pytorch", "torch", "PyTorch"},
            "langchain": {"langchain", "LangChain", "lang_chain"},
            "rag": {"rag", "RAG", "retrieval augmented generation"},
            "agent": {"agent", "Agent", "ai agent", "智能体"},
        }

        self._tech_categories: dict[str, list[str]] = {
            "编程语言": ["python", "java", "javascript", "typescript", "golang", "rust", "c++", "c#", "go", "php", "ruby", "swift", "kotlin"],
            "前端": ["vue", "react", "angular", "html", "css", "jquery", "bootstrap", "tailwind"],
            "后端": ["django", "flask", "fastapi", "spring", "node.js", "express", "rails", "gin"],
            "数据库": ["mysql", "postgresql", "mongodb", "redis", "elasticsearch", "cassandra", "sqlite"],
            "大数据": ["hadoop", "spark", "hive", "flink", "kafka", "storm", "airflow"],
            "AI/ML": ["tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy", "opencv", "nltk", "spacy", "langchain", "rag", "agent"],
            "DevOps": ["docker", "kubernetes", "jenkins", "gitlab", "ansible", "terraform", "prometheus", "grafana"],
            "云服务": ["aws", "azure", "gcp", "阿里云", "腾讯云", "华为云"],
        }

    def match(self, jd_requirement: str | list[str], resume_value: str | list) -> MatchResult:
        if isinstance(jd_requirement, str):
            jd_requirement = [jd_requirement]
        if isinstance(resume_value, str):
            resume_value = [resume_value]

        jd_techs = self._normalize_tech_names(jd_requirement)
        resume_techs = self._normalize_tech_names([v for v in resume_value if v])

        if not jd_techs:
            return MatchResult(score=1.0, matched=True, reason="无特定技术要求", confidence=1.0)

        matched = jd_techs & resume_techs
        missing = jd_techs - resume_techs
        extra = resume_techs - jd_techs

        score = len(matched) / len(jd_techs) if jd_techs else 1.0
        matched_flag = len(missing) == 0

        if matched_flag:
            reason = f"技术栈完全匹配: {len(matched)}/{len(jd_techs)}"
        else:
            reason = f"技术栈部分匹配: {len(matched)}/{len(jd_techs)}, 缺失: {', '.join(list(missing)[:3])}"

        return MatchResult(
            score=score,
            matched=matched_flag,
            reason=reason,
            confidence=0.95,
            details={
                "matched": list(matched),
                "missing": list(missing),
                "extra": list(extra)[:10],
            },
        )

    def _normalize_tech_names(self, techs: list[str]) -> set[str]:
        normalized: set[str] = set()
        for tech in techs:
            tech_lower = tech.lower().strip()
            normalized.add(tech_lower)
            if tech_lower in self._tech_synonyms:
                normalized.update(self._tech_synonyms[tech_lower])
            for synonyms in self._tech_synonyms.values():
                if tech_lower in synonyms:
                    normalized.add(tech_lower)
                    normalized.update(synonyms)
        return normalized

    def match_by_category(
        self, jd_techs: list[str], resume_techs: list[str]
    ) -> dict[str, MatchResult]:
        results = {}

        jd_normalized = self._normalize_tech_names(jd_techs)
        resume_normalized = self._normalize_tech_names([v for v in resume_techs if v])

        for category, category_techs in self._tech_categories.items():
            jd_in_category = jd_normalized & set(category_techs)
            resume_in_category = resume_normalized & set(category_techs)

            if not jd_in_category:
                continue

            matched = jd_in_category & resume_in_category
            score = len(matched) / len(jd_in_category) if jd_in_category else 1.0

            results[category] = MatchResult(
                score=score,
                matched=len(matched) > 0,
                reason=f"{category}: {len(matched)}/{len(jd_in_category)}",
                confidence=0.9,
                details={
                    "matched": list(matched),
                    "required": list(jd_in_category),
                },
            )

        return results
