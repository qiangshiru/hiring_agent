# 代码规范

## 目录
1. [类型注解](#类型注解)
2. [错误处理](#错误处理)
3. [日志规范](#日志规范)
4. [测试规范](#测试规范)
5. [代码风格](#代码风格)
6. [命名规范](#命名规范)
7. [文档规范](#文档规范)

## 类型注解

### 基本要求
- 所有函数/方法必须添加类型注解
- 所有变量尽可能添加类型注解
- 使用 `Optional[T]` 表示可空类型
- 使用 `Union[T, U]` 表示联合类型（Python 3.10+ 可用 `T | U`）

### 正确示例
```python
# ✅ 正确
def parse_jd(text: str) -> JDParseResult:
    """解析 JD 为结构化数据。"""
    if not text.strip():
        raise EmptyInputError("JD 文本不能为空")
    return self._extract_fields(text)

def get_users(limit: int = 10, offset: int = 0) -> list[User]:
    """获取用户列表。"""
    pass
```

### 错误示例
```python
# ❌ 错误
def parse(text):  # 缺少参数和返回值类型注解
    return data
```

### 复杂类型
```python
from typing import Optional, Dict, Any, Protocol

def process_items(items: list[Dict[str, Any]]) -> Optional[str]:
    """处理项目列表。"""
    pass

class LLMClient(Protocol):
    async def complete(self, prompt: str) -> str:
        raise NotImplementedError
```

## 错误处理

### 异常类定义
- 自定义异常必须继承自 `HiringAgentError` 或其子类
- 异常类应提供清晰的错误信息
- 可添加额外属性用于错误上下文

### 正确示例
```python
class JDParserError(HiringAgentError):
    """JD 解析基异常。"""
    pass

class FieldExtractionError(JDParserError):
    """字段提取失败。"""
    def __init__(self, field: str, reason: str):
        self.field = field
        self.reason = reason
        super().__init__(f"提取字段 {field} 失败: {reason}")
```

### 异常处理原则
- 捕获异常时要具体，避免使用 `except Exception`
- 在合适的层次处理异常，不要在底层吞掉异常
- 提供足够的错误上下文信息

```python
# ✅ 正确
try:
    result = await self._call_llm(prompt)
except APIError as e:
    logger.warning("LLM API 调用失败", error=str(e))
    return self._fallback_to_rules()
except TimeoutError:
    logger.warning("LLM 请求超时")
    return self._fallback_to_rules()

# ❌ 错误
try:
    result = await self._call_llm(prompt)
except Exception:  # 太宽泛
    return None
```

## 日志规范

### 日志工具
使用 `structlog` 作为日志工具：

```python
import structlog

logger = structlog.get_logger()
```

### 日志级别
- **DEBUG**: 详细的调试信息，生产环境禁用
- **INFO**: 正常的业务流程记录
- **WARNING**: 警告信息，可能需要关注
- **ERROR**: 错误信息，需要处理
- **EXCEPTION**: 异常信息，包含堆栈跟踪

### 日志格式
- 使用关键字参数传递结构化数据
- 日志消息使用小写字母，用下划线分隔
- 包含必要的上下文信息

```python
# ✅ 正确
logger.info(
    "jd_parsed",
    jd_id=jd.id,
    fields_extracted=len(result),
    duration_ms=duration,
)

logger.warning(
    "rule_failed",
    rule_id=rule.id,
    reason=result.reason,
)

logger.error(
    "api_call_failed",
    endpoint=url,
    status_code=response.status_code,
    error=str(exc),
)
```

### 避免的做法
```python
# ❌ 错误
logger.info(f"JD {jd.id} parsed successfully")  # 字符串格式化
logger.info("JD parsed", jd.id, len(result))     # 位置参数
```

## 测试规范

### 测试框架
使用 `pytest` 作为测试框架：

```python
import pytest
from unittest.mock import Mock, patch
```

### 测试类命名
测试类以 `Test` 开头，测试方法以 `test_` 开头：

```python
class TestJDParser:
    def test_parse_success(self, jd_parser):
        result = jd_parser.parse(SAMPLE_JD)
        assert result.技术栈.must == ["Python"]

    def test_empty_input_raises(self, jd_parser):
        with pytest.raises(EmptyInputError):
            jd_parser.parse("")

    @patch.object(LLMClient, "complete")
    def test_llm_failure_recovery(self, mock_complete, jd_parser):
        mock_complete.side_effect = APIError()
        # 验证降级到规则提取
        result = jd_parser.parse(SAMPLE_JD)
        assert result is not None
```

### Fixture 使用
使用 `@pytest.fixture` 定义测试夹具：

```python
@pytest.fixture
def jd_parser():
    return JDParserService()

@pytest.fixture
def sample_jd():
    return JDParseResult(
        工作经验=WorkExperienceRequirement(min_years=3),
        学历=EducationRequirement(必须=["本科"]),
    )
```

### 测试覆盖要点
- 正常路径测试
- 边界条件测试
- 异常处理测试
- 性能基准测试（使用 `@pytest.mark.slow` 标记）
- 集成测试（使用 `@pytest.mark.integration` 标记）

## 代码风格

### 代码格式化
使用 `black` 进行代码格式化：

```bash
black src/ tests/
```

### 代码检查
使用 `flake8` 进行代码检查：

```bash
flake8 src/ tests/
```

### 类型检查
使用 `mypy` 进行类型检查：

```bash
mypy src/
```

### 代码结构
- 一行不超过 120 个字符
- 使用空行分隔逻辑块
- 函数/方法不超过 50 行
- 类不超过 200 行

## 命名规范

### 变量命名
- 使用 snake_case
- 描述性命名，避免缩写

```python
# ✅ 正确
user_name = "张三"
max_retries = 3
jd_parse_result = parse_jd(text)

# ❌ 错误
un = "张三"
mr = 3
res = parse_jd(text)
```

### 函数/方法命名
- 使用 snake_case
- 动词开头

```python
# ✅ 正确
def parse_jd(text: str) -> JDParseResult:
    pass

def calculate_confidence(results: list) -> float:
    pass

# ❌ 错误
def JD(text: str):  # 大驼峰 + 不描述
    pass
```

### 类命名
- 使用 PascalCase
- 使用名词或名词短语

```python
# ✅ 正确
class JDParserService:
    pass

class ScreeningRule:
    pass

# ❌ 错误
class jd_parser:  # snake_case
    pass
```

### 常量命名
- 使用 UPPER_SNAKE_CASE

```python
# ✅ 正确
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# ❌ 错误
maxRetries = 3  # 驼峰命名
default_timeout = 30  # snake_case
```

## 文档规范

### 函数/方法文档
使用 Google 风格或 NumPy 风格的文档字符串：

```python
def parse_jd(text: str, use_cache: bool = True) -> JDParseResult:
    """解析 JD 文本为结构化数据。
    
    Args:
        text: JD 文本内容
        use_cache: 是否使用缓存（默认 True）
    
    Returns:
        解析后的 JDParseResult 对象
    
    Raises:
        EmptyInputError: JD 文本为空时抛出
        JDParserError: 解析失败时抛出
    
    Example:
        >>> result = parse_jd("招聘 Python 工程师")
        >>> result.技术栈.must
        ['Python']
    """
    pass
```

### 类文档
```python
class JDParserService:
    """JD 解析服务。
    
    提供 JD 文本解析功能，支持规则引擎和 LLM 两种模式。
    
    Attributes:
        _extractors: 字段提取器映射
        _llm_client: LLM 客户端
        _cache: 缓存实例
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        """初始化 JD 解析服务。
        
        Args:
            llm_client: LLM 客户端实例（可选）
        """
        pass
```

### 模块文档
在模块开头添加文档字符串：

```python
"""JD 解析服务模块。

提供 JD 文本解析功能，支持：
- 规则引擎解析
- LLM 解析
- 混合模式解析
- 结果缓存
"""
```
