from http import HTTPStatus
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class ApplicationError(Exception):
    """Base application exception with an HTTP representation."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


def build_error_response(
    *,
    request: Request,
    status_code: int,
    message: str,
    details: dict[str, Any] | list[Any] | None = None,
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "message": message,
                "details": details or {},
                "request_id": request_id,
            }
        },
    )


async def application_error_handler(request: Request, exc: ApplicationError) -> JSONResponse:
    return build_error_response(
        request=request,
        status_code=exc.status_code,
        message=exc.message,
        details=exc.details,
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return build_error_response(
        request=request,
        status_code=exc.status_code,
        message=str(exc.detail),
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return build_error_response(
        request=request,
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        message="Validation error",
        details=exc.errors(),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return build_error_response(
        request=request,
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        message="Internal server error",
    )
