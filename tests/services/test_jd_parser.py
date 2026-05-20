import pytest

from src.config import Settings
from src.schemas.jd import JDParseResult
from src.services.jd_parser.extractors import (
    CityExtractor,
    EducationExtractor,
    ExtractionContext,
    SalaryExtractor,
    TechStackExtractor,
    WorkExperienceExtractor,
)
from src.services.jd_parser.service import JDParseCache, JDParserService


class MemoryCache(JDParseCache):
    def __init__(self) -> None:
        self.values: dict[str, JDParseResult] = {}

    async def get(self, key: str) -> JDParseResult | None:
        return self.values.get(key)

    async def set(self, key: str, value: JDParseResult, ttl_seconds: int) -> None:
        self.values[key] = value


@pytest.fixture
def settings() -> Settings:
    return Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        redis_url="redis://localhost:6379/15",
        milvus_host="localhost",
        jd_parser_known_tech_stacks=["Python", "RAG", "LangChain", "Agent"],
        jd_parser_bonus_hints=["优先", "加分"],
        jd_parser_must_hints=["熟悉", "精通"],
        jd_parser_education_terms=["博士", "硕士", "本科", "大专", "985", "211", "统招"],
        jd_parser_city_terms=["北京", "上海", "广州", "深圳"],
    )


@pytest.fixture
def context(settings: Settings) -> ExtractionContext:
    return ExtractionContext(
        text="""
        招聘 Python AI 工程师：
        - 985优先
        - 3年以上经验
        - 熟悉 RAG
        - 熟悉 Agent
        - 熟悉 LangChain
        - 北京
        - AI行业经验
        - 30k-50k
        """,
        settings=settings,
    )


def test_education_extractor(context: ExtractionContext) -> None:
    result = EducationExtractor().extract(context)

    assert result.must == ["985"]
    assert result.bonus == ["211"]


def test_work_experience_extractor(context: ExtractionContext) -> None:
    result = WorkExperienceExtractor().extract(context)

    assert result.min_years == 3
    assert result.max_years is None


def test_tech_stack_extractor(context: ExtractionContext) -> None:
    result = TechStackExtractor().extract(context)

    assert result.must == ["Python", "RAG", "LangChain"]
    assert result.bonus == ["Agent"]


def test_city_and_salary_extractors(context: ExtractionContext) -> None:
    cities = CityExtractor().extract(context)
    salary = SalaryExtractor().extract(context)

    assert cities == ["北京"]
    assert salary is not None
    assert salary.min_monthly == 30000
    assert salary.max_monthly == 50000


def test_jd_parser_service_parse(settings: Settings) -> None:
    parser = JDParserService(settings=settings, cache=MemoryCache())

    result = parser.parse(
        """
        招聘 Python AI 工程师：
        - 985优先
        - 3年以上经验
        - 熟悉 RAG
        - 熟悉 Agent
        - 熟悉 LangChain
        """
    )

    assert result.技术栈.must == ["Python", "RAG", "LangChain"]
    assert result.技术栈.bonus == ["Agent"]
    assert result.工作经验.min_years == 3


@pytest.mark.asyncio
async def test_jd_parser_service_uses_cache(settings: Settings) -> None:
    cache = MemoryCache()
    parser = JDParserService(settings=settings, cache=cache)
    text = "招聘 Python 工程师，3年以上经验，北京，20k-30k"

    first_result = await parser.parse_async(text)
    second_result = await parser.parse_async(text)

    assert first_result == second_result
    assert len(cache.values) == 1
