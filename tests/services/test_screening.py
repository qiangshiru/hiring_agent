import pytest
from src.services.screening import ScreeningService


class TestScreeningService:
    @pytest.fixture
    def service(self):
        return ScreeningService()

    def test_screen_basic(self, service, sample_jd, sample_resume):
        result = service.screen(sample_jd, sample_resume)
        
        assert result is not None
        assert hasattr(result, "技术匹配度")
        assert hasattr(result, "AI能力深度")
        assert hasattr(result, "综合评分")

    def test_screen_technical_match(self, service, sample_jd, sample_resume):
        result = service.screen(sample_jd, sample_resume)
        
        assert 0 <= result.技术匹配度 <= 1
        assert result.技术匹配度 > 0

    def test_screen_ai_depth(self, service, sample_jd, sample_resume):
        result = service.screen(sample_jd, sample_resume)
        
        assert 0 <= result.AI能力深度 <= 1

    def test_screen_engineering_ability(self, service, sample_jd, sample_resume):
        result = service.screen(sample_jd, sample_resume)
        
        assert 0 <= result.工程能力 <= 1

    def test_screen_education(self, service, sample_jd, sample_resume):
        result = service.screen(sample_jd, sample_resume)
        
        assert 0 <= result.教育背景 <= 1

    def test_screen_stability(self, service, sample_jd, sample_resume):
        result = service.screen(sample_jd, sample_resume)
        
        assert 0 <= result.稳定性 <= 1

    def test_screen_overall_score(self, service, sample_jd, sample_resume):
        result = service.screen(sample_jd, sample_resume)
        
        assert 0 <= result.综合评分 <= 1

    def test_screen_result(self, service, sample_jd, sample_resume):
        result = service.screen(sample_jd, sample_resume)
        
        assert result.筛选结果 in ["通过", "待定", "不通过"]

    def test_screen_reasons(self, service, sample_jd, sample_resume):
        result = service.screen(sample_jd, sample_resume)
        
        assert isinstance(result.理由, list)

    def test_screen_high_match(self, service, sample_jd, sample_resume):
        result = service.screen(sample_jd, sample_resume)
        
        if result.综合评分 >= 0.7:
            assert result.筛选结果 == "通过"
