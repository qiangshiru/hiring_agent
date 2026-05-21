import pytest
from src.services.evaluation import EvaluationService, ReportGenerator


class TestEvaluationService:
    @pytest.fixture
    def service(self):
        return EvaluationService()

    def test_evaluate_basic(self, service, mock_interview_record):
        result = service.evaluate(mock_interview_record)
        
        assert result is not None
        assert hasattr(result, "技术深度")
        assert hasattr(result, "沟通表达")
        assert hasattr(result, "综合评分")

    def test_evaluate_tech_depth(self, service, mock_interview_record):
        result = service.evaluate(mock_interview_record)
        
        assert result.技术深度 is not None
        assert result.技术深度.level in ["强", "中", "弱"]
        assert 0 <= result.技术深度.score <= 10

    def test_evaluate_communication(self, service, mock_interview_record):
        result = service.evaluate(mock_interview_record)
        
        assert result.沟通表达 is not None
        assert result.沟通表达.level in ["强", "中", "弱"]

    def test_evaluate_authenticity(self, service, mock_interview_record):
        result = service.evaluate(mock_interview_record)
        
        assert result.真实性 is not None
        assert result.真实性.level in ["强", "中", "弱"]

    def test_evaluate_system_design(self, service, mock_interview_record):
        result = service.evaluate(mock_interview_record)
        
        assert result.系统设计 is not None
        assert result.系统设计.level in ["强", "中", "弱"]

    def test_evaluate_engineering(self, service, mock_interview_record):
        result = service.evaluate(mock_interview_record)
        
        assert result.工程能力 is not None
        assert result.工程能力.level in ["强", "中", "弱"]

    def test_evaluate_overall_score(self, service, mock_interview_record):
        result = service.evaluate(mock_interview_record)
        
        assert 0 <= result.综合评分 <= 100

    def test_evaluate_strengths(self, service, mock_interview_record):
        result = service.evaluate(mock_interview_record)
        
        assert isinstance(result.优势, list)

    def test_evaluate_weaknesses(self, service, mock_interview_record):
        result = service.evaluate(mock_interview_record)
        
        assert isinstance(result.不足, list)


class TestReportGenerator:
    @pytest.fixture
    def generator(self):
        return ReportGenerator()

    def test_generate_basic(self, generator, mock_interview_record):
        from src.services.evaluation import EvaluationService
        
        eval_service = EvaluationService()
        evaluation = eval_service.evaluate(mock_interview_record)
        
        from src.schemas.evaluation import RiskDetectionResult
        risk_result = RiskDetectionResult(risks=[], overall_risk_level="无")
        
        report = generator.generate("张三", evaluation, risk_result)
        
        assert report is not None
        assert report.candidate_name == "张三"
        assert hasattr(report, "evaluation_result")
        assert hasattr(report, "risk_result")

    def test_generate_recommendation(self, generator, mock_interview_record):
        from src.services.evaluation import EvaluationService
        from src.schemas.evaluation import RiskDetectionResult
        
        eval_service = EvaluationService()
        evaluation = eval_service.evaluate(mock_interview_record)
        evaluation.综合评分 = 85.0
        risk_result = RiskDetectionResult(risks=[], overall_risk_level="无")
        
        report = generator.generate("测试", evaluation, risk_result)
        
        assert report.hiring_recommendation in ["强烈推荐", "推荐", "谨慎推荐", "不推荐"]

    def test_generate_key_insights(self, generator, mock_interview_record):
        from src.services.evaluation import EvaluationService
        from src.schemas.evaluation import RiskDetectionResult
        
        eval_service = EvaluationService()
        evaluation = eval_service.evaluate(mock_interview_record)
        risk_result = RiskDetectionResult(risks=[], overall_risk_level="无")
        
        report = generator.generate("测试", evaluation, risk_result)
        
        assert isinstance(report.key_insights, list)
        assert len(report.key_insights) > 0
