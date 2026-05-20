import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")
os.environ.setdefault("MILVUS_HOST", "localhost")
os.environ.setdefault("LOG_JSON", "false")
os.environ.setdefault("JD_PARSER_KNOWN_TECH_STACKS", '["Python","RAG","LangChain","Agent"]')
os.environ.setdefault("JD_PARSER_BONUS_HINTS", '["优先","加分"]')
os.environ.setdefault("JD_PARSER_MUST_HINTS", '["熟悉","精通"]')
os.environ.setdefault("JD_PARSER_EDUCATION_TERMS", '["博士","硕士","本科","大专","985","211","统招"]')
os.environ.setdefault("JD_PARSER_CITY_TERMS", '["北京","上海","广州","深圳","杭州","南京","成都","武汉","西安","苏州","远程"]')


@pytest.fixture
def client() -> Iterator[TestClient]:
    from src.main import create_app

    with TestClient(create_app()) as test_client:
        yield test_client
