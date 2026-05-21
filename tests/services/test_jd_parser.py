import pytest
from src.services.jd_parser import JDParserService


class TestJDParserService:
    @pytest.fixture
    def service(self):
        return JDParserService()

    def test_parse_basic_jd(self, service):
        jd_text = """
        招聘 AI 工程师
        
        要求：
        - 本科及以上学历
        - 3 年以上工作经验
        - 熟练掌握 Python
        - 有 LangChain 开发经验优先
        """
        result = service.parse(jd_text)
        
        assert result is not None
        assert hasattr(result, "技术栈")
        assert hasattr(result, "学历")

    def test_parse_with_tech_stack(self, service):
        jd_text = """
        招聘 Python 工程师
        
        技术要求：
        - 必须：Python, LangChain, LLM
        - 加分：RAG, 向量数据库, Kubernetes
        """
        result = service.parse(jd_text)
        
        assert result.技术栈.必须 is not None
        assert len(result.技术栈.必须) >= 3

    def test_parse_experience_requirement(self, service):
        jd_text = """
        招聘高级工程师
        
        要求：
        - 5 年以上 Python 开发经验
        - 有大型项目经验
        """
        result = service.parse(jd_text)
        
        assert hasattr(result, "工作经验")
        assert result.工作经验.min_years is not None

    def test_parse_empty_text(self, service):
        result = service.parse("")
        assert result is not None

    def test_parse_education_requirement(self, service):
        jd_text = """
        招聘算法工程师
        
        学历要求：
        - 必须：本科（985/211 优先）
        - 加分：硕士、博士
        """
        result = service.parse(jd_text)
        
        assert hasattr(result, "学历")
        assert "本科" in result.学历.必须
