import time
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.api.v1.jd import router as jd_router
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
    resolved_settings = settings or get_settings()
    configure_logging(level=resolved_settings.log_level, json_logs=resolved_settings.log_json)
    database_engine = create_engine(resolved_settings)

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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.backend_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.middleware("http")(request_logging_middleware)

    app.add_exception_handler(ApplicationError, application_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    api_router = APIRouter(prefix=resolved_settings.api_v1_prefix)
    api_router.include_router(create_health_router())
    api_router.include_router(jd_router)
    app.include_router(api_router)

    @app.get("/", include_in_schema=False)
    async def root() -> dict[str, str]:
        return {"name": resolved_settings.app_name, "status": "ok"}

    return app


app = create_app()
