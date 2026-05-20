import json
from functools import lru_cache
from typing import Literal

from pydantic import AnyUrl, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or a .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="Hiring Agent", min_length=1)
    app_env: Literal["local", "test", "staging", "production"] = "local"
    app_debug: bool = False
    app_host: str = "0.0.0.0"
    app_port: int = Field(default=8000, ge=1, le=65535)
    api_v1_prefix: str = Field(default="/api/v1", pattern=r"^/.*")

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_json: bool = True

    backend_cors_origins: list[str] = Field(default_factory=list)

    database_url: str = Field(min_length=1)
    database_echo: bool = False
    database_pool_size: int = Field(default=5, ge=1)
    database_max_overflow: int = Field(default=10, ge=0)

    redis_url: str = Field(min_length=1)

    llm_provider: str = Field(default="openai", min_length=1)
    llm_api_key: SecretStr = Field(default=SecretStr(""))
    llm_model: str = Field(default="gpt-4o-mini", min_length=1)
    llm_base_url: AnyUrl | None = None
    llm_timeout_seconds: int = Field(default=30, ge=1, le=300)

    milvus_host: str = Field(min_length=1)
    milvus_port: int = Field(default=19530, ge=1, le=65535)
    milvus_user: str = ""
    milvus_password: SecretStr = Field(default=SecretStr(""))
    milvus_collection: str = Field(default="candidate_embeddings", min_length=1)

    jd_parser_mode: Literal["rule", "llm", "hybrid"] = "rule"
    jd_parser_cache_ttl_seconds: int = Field(default=3600, ge=0)
    jd_parser_llm_max_retries: int = Field(default=2, ge=0, le=5)
    jd_parser_known_tech_stacks: list[str] = Field(default_factory=list)
    jd_parser_bonus_hints: list[str] = Field(default_factory=list)
    jd_parser_must_hints: list[str] = Field(default_factory=list)
    jd_parser_education_terms: list[str] = Field(default_factory=list)
    jd_parser_city_terms: list[str] = Field(default_factory=list)

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> list[str]:
        if value is None or value == "":
            return []
        if isinstance(value, str):
            stripped_value = value.strip()
            if stripped_value.startswith("["):
                parsed_value = json.loads(stripped_value)
                if not isinstance(parsed_value, list):
                    raise ValueError("backend_cors_origins JSON value must be a list")
                return [str(origin) for origin in parsed_value]
            return [origin.strip() for origin in stripped_value.split(",") if origin.strip()]
        if isinstance(value, list):
            return [str(origin) for origin in value]
        raise ValueError("backend_cors_origins must be a list or comma-separated string")

    @field_validator(
        "jd_parser_known_tech_stacks",
        "jd_parser_bonus_hints",
        "jd_parser_must_hints",
        "jd_parser_education_terms",
        "jd_parser_city_terms",
        mode="before",
    )
    @classmethod
    def parse_string_list(cls, value: object) -> list[str]:
        if value is None or value == "":
            return []
        if isinstance(value, str):
            stripped_value = value.strip()
            if stripped_value.startswith("["):
                parsed_value = json.loads(stripped_value)
                if not isinstance(parsed_value, list):
                    raise ValueError("JSON value must be a list")
                return [str(item) for item in parsed_value]
            return [item.strip() for item in stripped_value.split(",") if item.strip()]
        if isinstance(value, list):
            return [str(item) for item in value]
        raise ValueError("value must be a list or comma-separated string")

    @field_validator("llm_base_url", mode="before")
    @classmethod
    def empty_llm_base_url_to_none(cls, value: object) -> object:
        if value == "":
            return None
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
