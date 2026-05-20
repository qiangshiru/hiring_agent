import pytest

from src.schemas.resume import ResumeParseResult
from src.services.resume_parser.extractors import (
    EducationExtractor,
    ExperienceExtractor,
    ProjectExtractor,
    SkillsExtractor,
)
from src.services.resume_parser.loaders import MarkdownLoader
from src.services.resume_parser.service import (
    NullResumeParseCache,
    ResumeParserService,
)


SAMPLE_RESUME_TEXT = """
张三
男 | 28岁 | 13812345678 | zhangsan@email.com | 北京

个人简历

教育背景
清华大学 计算机科学与技术 本科 2014-2018
北京大学 软件工程 硕士 2018-2021

工作经历
字节跳动 高级后端工程师 2021-至今
- 负责抖音推荐系统后端开发
- 使用 Python 和 Go 语言
- 熟悉 Redis, MySQL, Kafka

阿里巴巴 研发工程师 2019-2021 (实习)
- 参与电商平台开发
- 使用 Java Spring Boot

项目经验
电商推荐系统 2023
- 担任技术负责人
- 基于深度学习的个性化推荐
- 使用技术: Python, TensorFlow, Redis

智能客服系统 2022
- 核心模块开发
- 使用 NLP 技术处理用户问题
- 使用技术: Python, PyTorch, LangChain

技能证书
编程语言: Python, Java, Go, JavaScript
后端框架: Django, Flask, Spring Boot
数据库: MySQL, PostgreSQL, MongoDB, Redis
工具: Git, Docker, Kubernetes
AI: TensorFlow, PyTorch, LangChain, RAG

自我评价
热爱技术，有较强的学习能力和团队协作精神。
"""


@pytest.fixture
def service() -> ResumeParserService:
    return ResumeParserService(cache=NullResumeParseCache())


@pytest.fixture
def sample_resume_text() -> str:
    return SAMPLE_RESUME_TEXT


class TestResumeParserService:
    def test_parse_text_basic_fields(self, service: ResumeParserService, sample_resume_text: str) -> None:
        result = service.parse_text(sample_resume_text)

        assert result.姓名 == "张三"
        assert result.性别 == "男"
        assert result.邮箱 == "zhangsan@email.com"

    def test_parse_text_skills(self, service: ResumeParserService, sample_resume_text: str) -> None:
        result = service.parse_text(sample_resume_text)

        assert len(result.技能) > 0
        skill_names = [s.名称 for s in result.技能]
        assert "Python" in skill_names or "java" in [s.lower() for s in skill_names]

    def test_parse_text_education(self, service: ResumeParserService, sample_resume_text: str) -> None:
        result = service.parse_text(sample_resume_text)

        assert len(result.教育) > 0
        schools = [e.学校 for e in result.教育]
        assert any("清华" in school for school in schools if school)

    def test_parse_text_experience(self, service: ResumeParserService, sample_resume_text: str) -> None:
        result = service.parse_text(sample_resume_text)

        assert len(result.工作经验) > 0
        companies = [e.公司 for e in result.工作经验]
        assert any("字节" in company for company in companies if company)

    def test_parse_text_projects(self, service: ResumeParserService, sample_resume_text: str) -> None:
        result = service.parse_text(sample_resume_text)

        assert len(result.项目) > 0
        project_names = [p.项目名称 for p in result.项目]
        assert any("推荐" in name or "客服" in name for name in project_names if name)


class TestEducationExtractor:
    def test_extract_education(self) -> None:
        extractor = EducationExtractor()
        result = extractor.extract(SAMPLE_RESUME_TEXT)

        assert len(result) >= 1
        assert any("清华" in edu.学校 for edu in result if edu.学校)

    def test_extract_education_with_dates(self) -> None:
        extractor = EducationExtractor()
        result = extractor.extract(SAMPLE_RESUME_TEXT)

        assert len(result) > 0
        assert any(edu.开始时间 is not None for edu in result)


class TestExperienceExtractor:
    def test_extract_experience(self) -> None:
        extractor = ExperienceExtractor()
        result = extractor.extract(SAMPLE_RESUME_TEXT)

        assert len(result) > 0

    def test_extract_company(self) -> None:
        extractor = ExperienceExtractor()
        result = extractor.extract(SAMPLE_RESUME_TEXT)

        companies = [exp.公司 for exp in result if exp.公司]
        assert any("字节" in company for company in companies)


class TestProjectExtractor:
    def test_extract_projects(self) -> None:
        extractor = ProjectExtractor()
        result = extractor.extract(SAMPLE_RESUME_TEXT)

        assert len(result) > 0

    def test_extract_tech_stack(self) -> None:
        extractor = ProjectExtractor()
        result = extractor.extract(SAMPLE_RESUME_TEXT)

        assert len(result) > 0
        tech_stacks = [tech for proj in result for tech in proj.技术栈]
        assert any(tech in ["Python", "TensorFlow", "PyTorch"] for tech in tech_stacks)


class TestSkillsExtractor:
    def test_extract_skills(self) -> None:
        extractor = SkillsExtractor()
        result = extractor.extract(SAMPLE_RESUME_TEXT)

        assert len(result) > 0
        skill_names = [s.名称 for s in result]
        assert any("Python" in name or "Java" in name for name in skill_names)

    def test_skill_categories(self) -> None:
        extractor = SkillsExtractor()
        result = extractor.extract(SAMPLE_RESUME_TEXT)

        categories = {s.类别 for s in result if s.类别}
        assert len(categories) > 0


class TestMarkdownLoader:
    def test_load_markdown(self, tmp_path) -> None:
        loader = MarkdownLoader()
        test_file = tmp_path / "test_resume.md"
        test_file.write_text(SAMPLE_RESUME_TEXT)

        result = loader.load(test_file)

        assert result.content is not None
        assert "张三" in result.content
        assert result.file_type == "markdown"

    def test_load_text_file(self, tmp_path) -> None:
        loader = MarkdownLoader()
        test_file = tmp_path / "test_resume.txt"
        test_file.write_text(SAMPLE_RESUME_TEXT)

        result = loader.load(test_file)

        assert result.content is not None
        assert result.file_type == "text"

    def test_unsupported_format(self, tmp_path) -> None:
        from src.services.resume_parser.loaders import UnsupportedFormatError

        loader = MarkdownLoader()
        test_file = tmp_path / "test.pdf"

        with pytest.raises(UnsupportedFormatError):
            loader.load(test_file)


class TestParserIntegration:
    def test_full_parsing(self, service: ResumeParserService, sample_resume_text: str) -> None:
        result = service.parse_text(sample_resume_text)

        assert result.姓名 is not None
        assert len(result.技能) > 0
        assert len(result.项目) > 0
        assert len(result.教育) > 0
        assert len(result.工作经验) > 0

    def test_parse_empty_text(self, service: ResumeParserService) -> None:
        result = service.parse_text("")

        assert result.姓名 is None
        assert len(result.技能) == 0

    def test_parse_minimal_resume(self, service: ResumeParserService) -> None:
        minimal_text = "李四\nPython工程师\n熟悉Django"
        result = service.parse_text(minimal_text)

        assert result.姓名 is not None or "李四" in (result.原始文本 or "")


class TestAcceptanceCriteria:
    def test_supports_multiple_format_input(self, service: ResumeParserService, tmp_path) -> None:
        test_file = tmp_path / "resume.md"
        test_file.write_text(SAMPLE_RESUME_TEXT)

        result = service.parse_resume(test_file)

        assert result.姓名 is not None
        assert len(result.技能) > 0
        assert len(result.项目) > 0
