"""简历筛选相关接口

提供的端点：
- POST /screening/screen       : 对单份简历进行 JD 匹配筛选
- POST /screening/screen/batch : 批量筛选多份简历
"""

from fastapi import APIRouter, Depends, HTTPException

from src.schemas.jd import JDParseResult
from src.schemas.resume import ResumeParseResult
from src.schemas.screening import ScreeningResult
from src.services.screening import ScreeningService

router = APIRouter(prefix="/screening", tags=["screening"])


def get_screening_service() -> ScreeningService:
    """依赖注入：获取简历筛选服务实例"""
    return ScreeningService()


@router.post("/screen", response_model=ScreeningResult, summary="Screen a resume against a JD")
async def screen_resume(
    jd: JDParseResult,
    resume: ResumeParseResult,
    service: ScreeningService = Depends(get_screening_service),
) -> ScreeningResult:
    """根据 JD 要求对单份简历进行筛选匹配"""
    try:
        return service.screen(jd, resume)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/screen/batch", summary="Screen multiple resumes against a JD")
async def screen_batch(
    jd: JDParseResult,
    resumes: list[ResumeParseResult],
    service: ScreeningService = Depends(get_screening_service),
) -> list[ScreeningResult]:
    """批量筛选：对多份简历进行 JD 匹配，返回每份的筛选结果"""
    try:
        return service.screen_batch(jd, resumes)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
