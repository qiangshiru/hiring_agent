from src.config import Settings


def test_settings_parses_comma_separated_cors_origins() -> None:
    settings = Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        redis_url="redis://localhost:6379/15",
        milvus_host="localhost",
        backend_cors_origins="http://localhost:3000,http://localhost:8000",
    )

    assert settings.backend_cors_origins == [
        "http://localhost:3000",
        "http://localhost:8000",
    ]


def test_settings_loads_required_external_services() -> None:
    settings = Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        redis_url="redis://localhost:6379/15",
        milvus_host="milvus",
    )

    assert settings.database_url == "sqlite+aiosqlite:///:memory:"
    assert settings.redis_url == "redis://localhost:6379/15"
    assert settings.milvus_host == "milvus"
