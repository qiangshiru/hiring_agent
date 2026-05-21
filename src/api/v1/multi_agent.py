from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from src.schemas.jd import JDParseResult
from src.schemas.resume import ResumeParseResult
from src.agents.multi_agent.orchestrator import MultiAgentOrchestrator
from src.agents.workflows.full_interview import FullInterviewWorkflow

router = APIRouter(prefix="/multi-agent", tags=["multi-agent"])

orchestrator = MultiAgentOrchestrator()
workflow = FullInterviewWorkflow()


@router.post("/evaluate")
async def multi_agent_evaluate(jd: JDParseResult, resume: ResumeParseResult):
    try:
        result = orchestrator.run_full_interview(jd, resume)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"多 Agent 评估失败: {str(e)}")


@router.post("/full-interview")
async def full_interview(jd: JDParseResult, resume: ResumeParseResult):
    try:
        result = workflow.run(jd, resume)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"完整面试流程失败: {str(e)}")


@router.get("/status")
async def get_status():
    try:
        status = orchestrator.get_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")
