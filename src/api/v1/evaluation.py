"""面试评价与风险检测相关接口

提供的端点：
- POST /evaluation/evaluate        : 对面试记录进行综合评价打分
- POST /evaluation/detect-risks    : 检测面试过程中的风险项（诚信、合规等）
- POST /evaluation/generate-report : 生成完整的面试评估报告（含风险分析）
"""

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

# 全局服务实例
evaluation_service = EvaluationService()
risk_service = RiskDetectionService()
report_generator = ReportGenerator()
risk_agent = RiskAgent()


@router.post("/evaluate", response_model=EvaluationResult)
async def evaluate_interview(interview_record: InterviewRecord):
    """对完整面试记录进行多维度评价（技术能力、沟通能力、综合素质等）"""
    try:
        result = evaluation_service.evaluate(interview_record)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"评价失败: {str(e)}")


@router.post("/detect-risks", response_model=RiskDetectionResult)
async def detect_risks(interview_record: InterviewRecord, resume: Optional[ResumeParseResult] = None):
    """检测面试中的潜在风险（如诚信问题、简历造假、合规风险等）"""
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
    """调用风险分析 Agent 生成包含整体评价与风险分析的完整报告"""
    try:
        report = risk_agent.run_full_analysis(
            interview_record=interview_record,
            resume=resume,
            candidate_name=candidate_name,
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告生成失败: {str(e)}")
