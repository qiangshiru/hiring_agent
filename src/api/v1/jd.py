from fastapi import APIRouter, Depends

from src.schemas.jd import JDParseRequest, JDParseResponse
from src.services.jd_parser.service import JDParserService

router = APIRouter(prefix="/jd", tags=["jd-parser"])


def get_jd_parser_service() -> JDParserService:
    return JDParserService()


@router.post("/parse", response_model=JDParseResponse, summary="Parse a job description")
async def parse_jd(
    payload: JDParseRequest,
    service: JDParserService = Depends(get_jd_parser_service),
) -> JDParseResponse:
    result, cached = await service.parse_with_cache_status_async(
        payload.text,
        use_cache=payload.use_cache,
    )
    return JDParseResponse(data=result, cached=cached)
