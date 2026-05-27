"""简历解析服务。

负责将各种格式的简历文件（PDF、Word 等）解析为结构化的候选人数据，
提取姓名、联系方式、教育背景、工作经验、项目经验、技能等关键信息。
支持基于文件的加载解析和纯文本解析两种模式，并提供缓存机制。
"""

import asyncio
import hashlib
import re
import time
from collections.abc import Mapping
from pathlib import Path
from typing import BinaryIO, Protocol

try:
    from redis.asyncio import Redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from src.config import Settings, get_settings
from src.core.exceptions import ApplicationError
from src.core.logging import get_logger
from src.schemas.resume import ResumeParseResult
from src.services.resume_parser.extractors import (
    EducationExtractor,
    ExperienceExtractor,
    ProjectExtractor,
    SkillsExtractor,
)
from src.services.resume_parser.loaders import (
    DocumentLoaderRegistry,
    RawDocument,
    UnsupportedFormatError,
    create_default_registry,
)

logger = get_logger(__name__)


class ResumeParseCache(Protocol):
    """简历解析结果缓存协议，定义缓存的读写接口。"""

    async def get(self, key: str) -> ResumeParseResult | None:
        raise NotImplementedError

    async def set(self, key: str, value: ResumeParseResult, ttl_seconds: int) -> None:
        raise NotImplementedError


class NullResumeParseCache:
    """空缓存实现（不使用缓存时回退到此实现）。"""
    async def get(self, key: str) -> ResumeParseResult | None:
        return None

    async def set(self, key: str, value: ResumeParseResult, ttl_seconds: int) -> None:
        return None


class RedisResumeParseCache:
    """基于 Redis 的简历解析结果缓存实现。"""

    def __init__(self, redis_url: str) -> None:
        if not REDIS_AVAILABLE:
            raise ImportError("redis package is required for RedisJDParseCache")
        self._redis = Redis.from_url(redis_url, decode_responses=True)

    async def get(self, key: str) -> ResumeParseResult | None:
        try:
            cached_value = await self._redis.get(key)
            if cached_value is None:
                return None
            return ResumeParseResult.model_validate_json(cached_value)
        except Exception:
            logger.exception("Failed to read resume parse cache")
            return None

    async def set(self, key: str, value: ResumeParseResult, ttl_seconds: int) -> None:
        if ttl_seconds <= 0:
            return
        try:
            await self._redis.set(
                key,
                value.model_dump_json(by_alias=True),
                ex=ttl_seconds,
            )
        except Exception:
            logger.exception("Failed to write resume parse cache")


class ResumeParserService:
    """简历解析服务核心类。

    负责加载简历文件、预处理文本，然后通过多个提取器分别提取
    姓名、性别、年龄、联系方式、教育、工作经历、项目、技能、自我评价等字段。
    """

    def __init__(
        self,
        *,
        settings: Settings | None = None,
        loader_registry: DocumentLoaderRegistry | None = None,
        cache: ResumeParseCache | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._loader_registry = loader_registry or create_default_registry()
        self._cache = cache if cache is not None else NullResumeParseCache()

        self._education_extractor = EducationExtractor()
        self._experience_extractor = ExperienceExtractor()
        self._project_extractor = ProjectExtractor()
        self._skills_extractor = SkillsExtractor()

    def parse_resume(self, file_path: str | Path, *, use_cache: bool = True) -> ResumeParseResult:
        """解析简历文件为结构化数据（同步包装器）。

        Args:
            file_path: 简历文件路径
            use_cache: 是否使用缓存

        Returns:
            解析后的 ResumeParseResult 对象
        """
        try:
            running_loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.parse_resume_async(file_path, use_cache=use_cache))
        if running_loop.is_running():
            raise ApplicationError("ResumeParserService.parse_resume cannot be called inside a running event loop")
        return asyncio.run(self.parse_resume_async(file_path, use_cache=use_cache))

    async def parse_resume_async(
        self, file_path: str | Path, *, use_cache: bool = True
    ) -> ResumeParseResult:
        """异步解析简历文件，加载文档后预处理并逐字段提取。"""
        path = Path(file_path) if isinstance(file_path, str) else file_path
        if not path.exists():
            raise ApplicationError(f"File not found: {file_path}", status_code=404)

        cache_key = self._build_cache_key(str(path))
        if use_cache:
            cached_result = await self._cache.get(cache_key)
            if cached_result is not None:
                return cached_result

        start_time = time.time()

        raw_doc = self._load_document(path)
        cleaned_text = self._preprocess(raw_doc.content)

        result = ResumeParseResult(
            姓名=self._extract_name(cleaned_text),
            性别=self._extract_gender(cleaned_text),
            年龄=self._extract_age(cleaned_text),
            电话=self._extract_phone(cleaned_text),
            邮箱=self._extract_email(cleaned_text),
            城市=self._extract_city(cleaned_text),
            教育=self._education_extractor.extract(cleaned_text),
            工作经验=self._experience_extractor.extract(cleaned_text),
            项目=self._project_extractor.extract(cleaned_text),
            技能=self._skills_extractor.extract(cleaned_text),
            自我评价=self._extract_self_evaluation(cleaned_text),
            原始文本=cleaned_text,
            解析耗时_ms=int((time.time() - start_time) * 1000),
        )

        if use_cache:
            await self._cache.set(cache_key, result, self._settings.jd_parser_cache_ttl_seconds)

        return result

    def parse_text(self, text: str, *, use_cache: bool = False) -> ResumeParseResult:
        """解析纯文本简历内容（不经过文件加载步骤）。"""
        start_time = time.time()
        cleaned_text = self._preprocess(text)

        return ResumeParseResult(
            姓名=self._extract_name(cleaned_text),
            性别=self._extract_gender(cleaned_text),
            年龄=self._extract_age(cleaned_text),
            电话=self._extract_phone(cleaned_text),
            邮箱=self._extract_email(cleaned_text),
            城市=self._extract_city(cleaned_text),
            教育=self._education_extractor.extract(cleaned_text),
            工作经验=self._experience_extractor.extract(cleaned_text),
            项目=self._project_extractor.extract(cleaned_text),
            技能=self._skills_extractor.extract(cleaned_text),
            自我评价=self._extract_self_evaluation(cleaned_text),
            原始文本=cleaned_text,
            解析耗时_ms=int((time.time() - start_time) * 1000),
        )

    def _load_document(self, path: Path) -> RawDocument:
        """根据文件扩展名选择对应加载器读取文档内容。"""
        try:
            return self._loader_registry.load(path)
        except UnsupportedFormatError:
            raise ApplicationError(f"Unsupported file format: {path.suffix}", status_code=400)
        except Exception as exc:
            raise ApplicationError(f"Failed to load document: {exc}", status_code=422)

    def _preprocess(self, text: str) -> str:
        """文本预处理：统一换行符、压缩空格、合并多余空行。"""
        text = re.sub(r"\r\n", "\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = text.strip()
        return text

    def _extract_name(self, text: str) -> str | None:
        """通过正则匹配提取候选人姓名（支持"姓名："标签、简历开头、独立行等格式）。"""
        patterns = [
            r"姓\s*名\s*[:：]?\s*([^\n,，]+)",
            r"([\u4e00-\u9fa5]{2,4})\s*(?:简历|CV|个人简历)",
            r"^([\u4e00-\u9fa5]{2,4})$",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                name = match.group(1).strip()
                if 2 <= len(name) <= 4:
                    return name
        return None

    def _extract_gender(self, text: str) -> str | None:
        """通过正则匹配提取性别信息。"""
        patterns = [
            r"性\s*别\s*[:：]\s*([男女])",
            r"(男|女)\s*生",
            r"(?:性别|sex)\s*[:：]?\s*([男女])",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None

    def _extract_age(self, text: str) -> int | None:
        """提取年龄，支持直接年龄标注或通过出生年份推算。"""
        patterns = [
            r"年\s*龄\s*[:：]\s*(\d+)",
            r"(\d{4})\s*年\s*生",
            r"(?:age|年龄)\s*[:：]?\s*(\d+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) >= 1:
                    value = match.group(1)
                    if len(value) == 4:
                        from datetime import datetime
                        return datetime.now().year - int(value)
                    elif len(value) <= 2:
                        return int(value)
        return None

    def _extract_phone(self, text: str) -> str | None:
        """提取手机号码（支持大陆手机号、+86 前缀、带分隔符等格式）。"""
        patterns = [
            r"1[3-9]\d[\s-]?\d{4}[\s-]?\d{4}",
            r"\+86[\s-]?1[3-9]\d[\s-]?\d{4}[\s-]?\d{4}",
            r"\d{3,4}[\s-]?\d{7,8}",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                phone = re.sub(r"[\s-]", "", match.group(0))
                if len(phone) >= 10:
                    return phone
        return None

    def _extract_email(self, text: str) -> str | None:
        """通过标准邮箱正则提取邮箱地址。"""
        pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        match = re.search(pattern, text)
        if match:
            return match.group(0)
        return None

    def _extract_city(self, text: str) -> str | None:
        """从文本前 500 个字符中匹配常见城市名称。"""
        common_cities = [
            "北京", "上海", "广州", "深圳", "杭州", "南京", "成都", "武汉",
            "西安", "苏州", "天津", "重庆", "厦门", "长沙", "郑州", "青岛",
        ]
        for city in common_cities:
            if city in text[:500]:
                return city
        return None

    def _extract_self_evaluation(self, text: str) -> str | None:
        """提取自我评价/个人简介段落，截取前 500 个字符。"""
        patterns = [
            r"(?:自我评价|个人评价|简介)(.*?)(?:\n\n|工作经历|项目经验|教育背景|$)",
            r"(?:About me|About|个人简介)(.*?)(?:\n\n|Experience|Project|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                evaluation = match.group(1).strip()
                if len(evaluation) >= 10:
                    return evaluation[:500]
        return None

    def _build_cache_key(self, file_path: str) -> str:
        """构建缓存键，基于文件路径、修改时间和文件大小的哈希值。"""
        path = Path(file_path)
        if path.exists():
            file_stat = path.stat()
            key_material = f"{file_path}:{file_stat.st_mtime}:{file_stat.st_size}"
        else:
            key_material = file_path
        digest = hashlib.sha256(key_material.encode("utf-8")).hexdigest()
        return f"resume_parser:{digest}"
