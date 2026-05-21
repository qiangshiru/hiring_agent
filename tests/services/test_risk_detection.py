import pytest
from src.services.risk_detection import RiskDetectionService


class TestRiskDetectionService:
    @pytest.fixture
    def service(self):
        return RiskDetectionService()

    def test_detect_basic(self, service, mock_interview_record, sample_resume):
        result = service.detect(mock_interview_record, sample_resume)
        
        assert result is not None
        assert hasattr(result, "risks")
        assert hasattr(result, "overall_risk_level")

    def test_detect_no_risks(self, service, mock_interview_record, sample_resume):
        result = service.detect(mock_interview_record, sample_resume)
        
        assert isinstance(result.risks, list)
        assert result.overall_risk_level in ["高", "中", "低", "无"]

    def test_detect_risk_types(self, service, mock_interview_record, sample_resume):
        result = service.detect(mock_interview_record, sample_resume)
        
        for risk in result.risks:
            assert risk.risk_type in ["项目造假", "过度包装", "死记硬背", "不稳定"]

    def test_detect_risk_levels(self, service, mock_interview_record, sample_resume):
        result = service.detect(mock_interview_record, sample_resume)
        
        for risk in result.risks:
            assert risk.risk_level in ["高", "中", "低"]

    def test_detect_risk_evidence(self, service, mock_interview_record, sample_resume):
        result = service.detect(mock_interview_record, sample_resume)
        
        for risk in result.risks:
            assert isinstance(risk.evidence, list)
            if len(risk.evidence) > 0:
                assert risk.evidence[0].source is not None
                assert risk.evidence[0].content is not None

    def test_detect_risk_confidence(self, service, mock_interview_record, sample_resume):
        result = service.detect(mock_interview_record, sample_resume)
        
        for risk in result.risks:
            assert 0 <= risk.confidence <= 1

    def test_detect_summary(self, service, mock_interview_record, sample_resume):
        result = service.detect(mock_interview_record, sample_resume)
        
        assert isinstance(result.risk_summary, str)

    def test_detect_without_resume(self, service, mock_interview_record):
        result = service.detect(mock_interview_record, None)
        
        assert result is not None
        assert isinstance(result.risks, list)

    def test_detect_empty_interview(self, service, sample_resume):
        from src.schemas.evaluation import InterviewRecord
        from datetime import datetime
        
        empty_interview = InterviewRecord(
            session_id="empty",
            jd_id="jd",
            resume_id="resume",
            turns=[],
            start_time=datetime.now(),
        )
        
        result = service.detect(empty_interview, sample_resume)
        
        assert result is not None
