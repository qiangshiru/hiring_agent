"""职位描述（JD）解析相关接口

提供的端点：
- POST /jd/parse : 解析职位描述文本，返回结构化数据
"""

from fastapi import APIRouter, Depends

from src.schemas.jd import JDParseRequest, JDParseResponse
from src.services.jd_parser.service import JDParserService

router = APIRouter(prefix="/jd", tags=["jd-parser"])


def get_jd_parser_service() -> JDParserService:
    """依赖注入：获取 JD 解析服务实例"""
    return JDParserService()


@router.post("/parse", response_model=JDParseResponse, summary="Parse a job description")
async def parse_jd(
    payload: JDParseRequest,
    service: JDParserService = Depends(get_jd_parser_service),
) -> JDParseResponse:
    """解析职位描述文本，支持缓存，返回结构化解析结果"""
    result, cached = await service.parse_with_cache_status_async(
        payload.text,
        use_cache=payload.use_cache,
    )
    return JDParseResponse(data=result, cached=cached)
