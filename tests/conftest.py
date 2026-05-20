import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")
os.environ.setdefault("MILVUS_HOST", "localhost")
os.environ.setdefault("LOG_JSON", "false")


@pytest.fixture
def client() -> Iterator[TestClient]:
    from src.main import create_app

    with TestClient(create_app()) as test_client:
        yield test_client
