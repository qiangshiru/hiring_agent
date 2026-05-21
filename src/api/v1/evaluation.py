from fastapi import APIRouter, HTTPException
from typing import Optional

from src.schemas.evaluation import (
    InterviewRecord,
    EvaluationResult,
    RiskDetectionResult,
    EvaluationReport,
)
from src.schemas.resume import ResumeParseResult
from src.services.evaluation import EvaluationService, ReportGenerator
from src.services.risk_detection import RiskDetectionService
from src.agents.risk_agent import RiskAgent

router = APIRouter(prefix="/evaluation", tags=["evaluation"])

evaluation_service = EvaluationService()
risk_service = RiskDetectionService()
report_generator = ReportGenerator()
risk_agent = RiskAgent()


@router.post("/evaluate", response_model=EvaluationResult)
async def evaluate_interview(interview_record: InterviewRecord):
    try:
        result = evaluation_service.evaluate(interview_record)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"评价失败: {str(e)}")


@router.post("/detect-risks", response_model=RiskDetectionResult)
async def detect_risks(interview_record: InterviewRecord, resume: Optional[ResumeParseResult] = None):
    try:
        result = risk_service.detect(interview_record, resume)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"风险检测失败: {str(e)}")


@router.post("/generate-report", response_model=EvaluationReport)
async def generate_evaluation_report(
    interview_record: InterviewRecord,
    resume: Optional[ResumeParseResult] = None,
    candidate_name: str = "候选人",
):
    try:
        report = risk_agent.run_full_analysis(
            interview_record=interview_record,
            resume=resume,
            candidate_name=candidate_name,
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告生成失败: {str(e)}")
