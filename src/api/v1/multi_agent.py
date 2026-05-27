"""多 Agent 协同面试相关接口

提供的端点：
- POST /multi-agent/evaluate        : 多 Agent（HR/Tech/Architect/Risk）协同评估候选人
- POST /multi-agent/full-interview   : 运行完整的多 Agent 面试流程
- GET  /multi-agent/status          : 查看多 Agent 系统运行状态
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from src.schemas.jd import JDParseResult
from src.schemas.resume import ResumeParseResult
from src.agents.multi_agent.orchestrator import MultiAgentOrchestrator
from src.agents.workflows.full_interview import FullInterviewWorkflow

router = APIRouter(prefix="/multi-agent", tags=["multi-agent"])

# 全局编排器与工作流实例，供所有请求复用
orchestrator = MultiAgentOrchestrator()
workflow = FullInterviewWorkflow()


@router.post("/evaluate")
async def multi_agent_evaluate(jd: JDParseResult, resume: ResumeParseResult):
    """运行多 Agent（HR、技术、架构、风险）协同评估流程"""
    try:
        result = orchestrator.run_full_interview(jd, resume)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"多 Agent 评估失败: {str(e)}")


@router.post("/full-interview")
async def full_interview(jd: JDParseResult, resume: ResumeParseResult):
    """运行完整的多 Agent 面试工作流，生成面试题目并评估"""
    try:
        result = workflow.run(jd, resume)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"完整面试流程失败: {str(e)}")


@router.get("/status")
async def get_status():
    """查询多 Agent 系统当前运行状态"""
    try:
        status = orchestrator.get_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")
