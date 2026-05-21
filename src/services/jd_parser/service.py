import asyncio
import hashlib
from collections.abc import Mapping
from typing import Protocol, cast, TypeVar, Optional

from redis.asyncio import Redis

from src.config import Settings, get_settings
from src.core.exceptions import ApplicationError
from src.core.logging import get_logger
from src.schemas.jd import JDParseResult
from src.services.jd_parser.extractors import (
    BaseExtractor,
    ExtractionContext,
    default_extractors,
)
from src.services.jd_parser.prompts import build_jd_parser_prompt, jd_parser_json_schema

logger = get_logger(__name__)
T = TypeVar("T")


class LLMClient(Protocol):
    async def complete_json(
        self,
        *,
        prompt: str,
        json_schema: dict[str, object],
        timeout_seconds: int,
    ) -> dict[str, object]:
        raise NotImplementedError


class JDParseCache(Protocol):
    async def get(self, key: str) -> Optional[JDParseResult]:
        raise NotImplementedError

    async def set(self, key: str, value: JDParseResult, ttl_seconds: int) -> None:
        raise NotImplementedError


class NullJDParseCache:
    async def get(self, key: str) -> Optional[JDParseResult]:
        return None

    async def set(self, key: str, value: JDParseResult, ttl_seconds: int) -> None:
        return None


class RedisJDParseCache:
    def __init__(self, redis_url: str) -> None:
        self._redis = Redis.from_url(redis_url, decode_responses=True)

    async def get(self, key: str) -> Optional[JDParseResult]:
        try:
            cached_value = await self._redis.get(key)
            if cached_value is None:
                return None
            return JDParseResult.model_validate_json(cached_value)
        except Exception:
            logger.exception("Failed to read JD parse cache")
            return None

    async def set(self, key: str, value: JDParseResult, ttl_seconds: int) -> None:
        if ttl_seconds <= 0:
            return
        try:
            await self._redis.set(
                key,
                value.model_dump_json(by_alias=True),
                ex=ttl_seconds,
            )
        except Exception:
            logger.exception("Failed to write JD parse cache")


class JDParserService:
    def __init__(
        self,
        *,
        settings: Optional[Settings] = None,
        extractors: Optional[Mapping[str, BaseExtractor[object]]] = None,
        llm_client: Optional[LLMClient] = None,
        cache: Optional[JDParseCache] = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._extractors = dict(extractors or default_extractors())
        self._llm_client = llm_client
        self._cache = cache if cache is not None else RedisJDParseCache(self._settings.redis_url)

    def parse(self, text: str, *, use_cache: bool = True) -> JDParseResult:
        """解析 JD 文本为结构化数据。
        
        Args:
            text: JD 文本内容
            use_cache: 是否使用缓存
        
        Returns:
            解析后的 JDParseResult 对象
        
        Raises:
            ApplicationError: JD 文本为空或解析失败
        """
        try:
            running_loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.parse_async(text, use_cache=use_cache))
        if running_loop.is_running():
            raise ApplicationError("JDParserService.parse cannot be called inside a running event loop")
        return asyncio.run(self.parse_async(text, use_cache=use_cache))

    async def parse_async(self, text: str, *, use_cache: bool = True) -> JDParseResult:
        """异步解析 JD 文本。"""
        result, _ = await self.parse_with_cache_status_async(text, use_cache=use_cache)
        return result

    async def parse_with_cache_status_async(
        self,
        text: str,
        *,
        use_cache: bool = True,
    ) -> tuple[JDParseResult, bool]:
        normalized_text = text.strip()
        if not normalized_text:
            raise ApplicationError("JD text cannot be empty", status_code=400)

        cache_key = self._build_cache_key(normalized_text)
        if use_cache:
            cached_result = await self._cache.get(cache_key)
            if cached_result is not None:
                logger.info(
                    "jd_parse_cache_hit",
                    cache_key=cache_key[:16],
                )
                return cached_result, True

        result = self._parse_with_rules(normalized_text)
        if self._settings.jd_parser_mode in {"llm", "hybrid"}:
            result = await self._merge_llm_result(normalized_text, result)

        if use_cache:
            await self._cache.set(cache_key, result, self._settings.jd_parser_cache_ttl_seconds)
            logger.info(
                "jd_parse_cache_miss",
                cache_key=cache_key[:16],
                mode=self._settings.jd_parser_mode,
            )
        return result, False

    def _parse_with_rules(self, text: str) -> JDParseResult:
        """使用规则引擎解析 JD。"""
        context = ExtractionContext(text=text, settings=self._settings)
        return JDParseResult(
            学历=self._extract("education", context),
            工作经验=self._extract("work_experience", context),
            技术栈=self._extract("tech_stack", context),
            行业经验=self._extract("industry_experience", context),
            城市要求=self._extract("city", context),
            薪资范围=self._extract("salary", context),
        )

    async def _merge_llm_result(self, text: str, rule_result: JDParseResult) -> JDParseResult:
        """合并规则解析结果与 LLM 解析结果。"""
        if self._llm_client is None:
            if self._settings.jd_parser_mode == "llm":
                raise ApplicationError("LLM client is not configured", status_code=503)
            return rule_result

        llm_result = await self._call_llm_with_retry(text)
        if self._settings.jd_parser_mode == "llm":
            return llm_result

        return JDParseResult(
            学历=llm_result.学历 if llm_result.学历.must or llm_result.学历.bonus else rule_result.学历,
            工作经验=llm_result.工作经验
            if llm_result.工作经验.min_years is not None
            else rule_result.工作经验,
            技术栈=llm_result.技术栈 if llm_result.技术栈.must or llm_result.技术栈.bonus else rule_result.技术栈,
            行业经验=llm_result.行业经验 or rule_result.行业经验,
            城市要求=llm_result.城市要求 or rule_result.城市要求,
            薪资范围=llm_result.薪资范围 or rule_result.薪资范围,
        )

    async def _call_llm_with_retry(self, text: str) -> JDParseResult:
        """调用 LLM 并处理重试逻辑。"""
        prompt = build_jd_parser_prompt(text)
        last_error: Optional[Exception] = None
        
        for attempt in range(self._settings.jd_parser_llm_max_retries + 1):
            try:
                assert self._llm_client is not None
                payload = await asyncio.wait_for(
                    self._llm_client.complete_json(
                        prompt=prompt,
                        json_schema=jd_parser_json_schema(),
                        timeout_seconds=self._settings.llm_timeout_seconds,
                    ),
                    timeout=self._settings.llm_timeout_seconds,
                )
                result = JDParseResult.model_validate(payload)
                logger.info(
                    "jd_parse_llm_success",
                    attempt=attempt + 1,
                    fields_extracted=len(result.model_dump()),
                )
                return result
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "jd_parse_llm_failure",
                    attempt=attempt + 1,
                    error=str(exc),
                )
        
        raise ApplicationError(
            "JD parser LLM extraction failed",
            status_code=503,
            details={"reason": str(last_error) if last_error else "unknown"},
        )

    def _extract(self, name: str, context: ExtractionContext) -> T:
        """执行字段提取。"""
        extractor = self._extractors[name]
        return cast(T, extractor.extract(context))

    def _build_cache_key(self, text: str) -> str:
        """构建缓存键。"""
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return f"jd_parser:{self._settings.jd_parser_mode}:{digest}"
