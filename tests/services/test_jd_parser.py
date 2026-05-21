import pytest
from unittest.mock import Mock, patch

from src.services.jd_parser import JDParserService
from src.schemas.jd import JDParseResult, WorkExperienceRequirement, EducationRequirement, TechStackRequirement


SAMPLE_JD = """
招聘 AI 工程师

要求：
- 本科及以上学历
- 3 年以上工作经验
- 熟练掌握 Python, LangChain
- 有 RAG 开发经验优先
"""

EMPTY_JD = ""


class TestJDParserService:
    @pytest.fixture
    def service(self):
        return JDParserService()

    def test_parse_success(self, service):
        """测试正常解析 JD。"""
        result = service.parse(SAMPLE_JD)
        
        assert result is not None
        assert isinstance(result, JDParseResult)
        assert hasattr(result, "技术栈")
        assert hasattr(result, "学历")
        assert hasattr(result, "工作经验")

    def test_parse_empty_input_raises(self, service):
        """测试空输入抛出异常。"""
        with pytest.raises(Exception):
            service.parse(EMPTY_JD)

    def test_parse_with_tech_stack(self, service):
        """测试解析技术栈字段。"""
        result = service.parse(SAMPLE_JD)
        
        assert result.技术栈 is not None
        assert isinstance(result.技术栈, TechStackRequirement)

    def test_parse_experience_requirement(self, service):
        """测试解析工作经验要求。"""
        result = service.parse(SAMPLE_JD)
        
        assert result.工作经验 is not None
        assert isinstance(result.工作经验, WorkExperienceRequirement)

    def test_parse_education_requirement(self, service):
        """测试解析学历要求。"""
        result = service.parse(SAMPLE_JD)
        
        assert result.学历 is not None
        assert isinstance(result.学历, EducationRequirement)

    @patch("src.services.jd_parser.service.RedisJDParseCache")
    def test_parse_uses_cache(self, mock_cache_class, service):
        """测试缓存机制。"""
        mock_cache = Mock()
        mock_cache_class.return_value = mock_cache
        mock_cache.get.return_value = None
        
        service.parse(SAMPLE_JD, use_cache=True)
        
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_called_once()

    @patch("src.services.jd_parser.service.RedisJDParseCache")
    def test_cache_hit_returns_cached_result(self, mock_cache_class, service):
        """测试缓存命中返回缓存结果。"""
        mock_cache = Mock()
        mock_cache_class.return_value = mock_cache
        expected_result = JDParseResult()
        mock_cache.get.return_value = expected_result
        
        result = service.parse(SAMPLE_JD, use_cache=True)
        
        assert result == expected_result
        mock_cache.set.assert_not_called()

    def test_parse_without_cache(self, service):
        """测试不使用缓存。"""
        result = service.parse(SAMPLE_JD, use_cache=False)
        
        assert result is not None
        assert isinstance(result, JDParseResult)

    def test_parse_with_extractors(self):
        """测试使用自定义提取器。"""
        from src.services.jd_parser.extractors import default_extractors
        
        extractors = default_extractors()
        service = JDParserService(extractors=extractors)
        
        result = service.parse(SAMPLE_JD)
        
        assert result is not None
