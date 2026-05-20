import logging
import sys
from contextvars import ContextVar
from typing import Any
from uuid import uuid4

from pythonjsonlogger import jsonlogger

request_id_context: ContextVar[str | None] = ContextVar("request_id", default=None)


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_context.get() or "-"
        return True


def new_request_id() -> str:
    return str(uuid4())


def set_request_id(request_id: str) -> None:
    request_id_context.set(request_id)


def configure_logging(*, level: str, json_logs: bool) -> None:
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(RequestIdFilter())

    if json_logs:
        formatter: logging.Formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s [%(request_id)s] %(name)s: %(message)s"
        )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_extra(**kwargs: Any) -> dict[str, Any]:
    return {"extra": kwargs}
