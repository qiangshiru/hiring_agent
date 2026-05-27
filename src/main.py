"""
Hiring Agent — FastAPI 应用入口。

模块职责：
1. 创建并配置 FastAPI 应用实例
2. 注册所有 API 路由（JD 解析 / 简历解析 / 筛选 / 评分 / 面试 / 多 Agent 评估 / 评价）
3. 配置中间件（CORS、请求日志）
4. 注册全局异常处理器
5. 提供健康检查端点（含数据库连通性检测）

路由注册清单（共 10 个模块）：
- health             GET  /api/v1/health
- jd_router           JD 解析          POST /api/v1/jd/parse
- resume_router       简历解析         POST /api/v1/resume/parse, /parse/file
- questions_router    面试题生成       POST /api/v1/questions/generate
- screening_router    简历筛选         POST /api/v1/screening/screen, /screen/batch
- scoring_router      简历评分         POST /api/v1/scoring/score, /score/batch, /score/weights
- interview_rest_router  面试会话 REST  POST/GET /api/v1/interview/session/...
- interview_ws_router    面试 WebSocket WS /api/v1/interview/ws/{session_id}
- multi_agent_router  多Agent协同评估  POST /api/v1/multi-agent/evaluate, /full-interview
- evaluation_router   面试评价/风险    POST /api/v1/evaluation/evaluate, /detect-risks, /generate-report
"""

import time
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

# ── API 路由模块 ──────────────────────────────────────────────
from src.api.v1.evaluation import router as evaluation_router
from src.api.v1.interview_rest import router as interview_rest_router
from src.api.v1.interview_ws import router as interview_ws_router
from src.api.v1.jd import router as jd_router
from src.api.v1.multi_agent import router as multi_agent_router
from src.api.v1.questions import router as questions_router
from src.api.v1.resume import router as resume_router
from src.api.v1.scoring import router as scoring_router
from src.api.v1.screening import router as screening_router

# ── 基础设施 ──────────────────────────────────────────────────
from src.config import Settings, get_settings
from src.core.exceptions import (
    ApplicationError,
    application_error_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_error_handler,
)
from src.core.logging import configure_logging, get_logger, log_extra, new_request_id, set_request_id
from src.database import create_engine

logger = get_logger(__name__)


def create_health_router() -> APIRouter:
    """创建健康检查路由，验证 API 和数据库连接均可用。"""
    router = APIRouter(tags=["health"])

    @router.get("/health", name="health")
    async def health_check(request: Request) -> dict[str, str]:
        try:
            async with request.app.state.engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
        except Exception:
            logger.exception("Database health check failed")
            return {"status": "degraded", "database": "unavailable"}
        return {"status": "ok", "database": "ok"}

    return router


async def request_logging_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """请求日志中间件：为每个请求生成唯一 ID，记录请求耗时和状态码。"""
    request_id = request.headers.get("X-Request-ID") or new_request_id()
    set_request_id(request_id)
    request.state.request_id = request_id
    started_at = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        elapsed_ms = round((time.perf_counter() - started_at) * 1000, 2)
        logger.exception(
            "Request failed",
            **log_extra(
                method=request.method,
                path=request.url.path,
                elapsed_ms=elapsed_ms,
            ),
        )
        raise

    elapsed_ms = round((time.perf_counter() - started_at) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "Request completed",
        **log_extra(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            elapsed_ms=elapsed_ms,
        ),
    )
    return response


def create_app(settings: Settings | None = None) -> FastAPI:
    """工厂函数：创建并配置完整的 FastAPI 应用。

    按以下顺序完成初始化：
    1. 解析配置、初始化日志和数据库引擎
    2. 注册 lifespan（管理数据库连接生命周期）
    3. 添加中间件（CORS → 请求日志）
    4. 注册全局异常处理器
    5. 挂载所有业务路由到 /api/v1 前缀下
    """
    resolved_settings = settings or get_settings()
    configure_logging(level=resolved_settings.log_level, json_logs=resolved_settings.log_json)
    database_engine = create_engine(resolved_settings)

    # ── 应用生命周期：启动时注入数据库引擎，关闭时释放连接 ──
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.engine = database_engine
        try:
            yield
        finally:
            await database_engine.dispose()

    app = FastAPI(
        title=resolved_settings.app_name,
        debug=resolved_settings.app_debug,
        version="0.1.0",
        lifespan=lifespan,
    )

    # ── 中间件（按添加顺序执行：CORS → 日志） ──
    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.backend_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.middleware("http")(request_logging_middleware)

    # ── 全局异常处理 ──
    app.add_exception_handler(ApplicationError, application_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # ── 注册所有业务路由 ──
    api_router = APIRouter(prefix=resolved_settings.api_v1_prefix)
    api_router.include_router(create_health_router())
    api_router.include_router(jd_router)                 # JD 解析
    api_router.include_router(resume_router)              # 简历解析
    api_router.include_router(questions_router)           # 面试题生成
    api_router.include_router(multi_agent_router)         # 多 Agent 评估
    api_router.include_router(interview_rest_router)      # 面试 REST API
    api_router.include_router(interview_ws_router)        # 面试 WebSocket
    api_router.include_router(screening_router)           # 简历筛选
    api_router.include_router(scoring_router)             # 简历评分
    api_router.include_router(evaluation_router)          # 面试评价与风险检测
    app.include_router(api_router)

    @app.get("/", include_in_schema=False)
    async def root() -> dict[str, str]:
        return {"name": resolved_settings.app_name, "status": "ok"}

    return app


app = create_app()
