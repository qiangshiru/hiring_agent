# Hiring Agent

企业级 AI 招聘系统后端基线，基于 FastAPI、SQLAlchemy 2.0 Async、Pydantic Settings 与 Alembic。

## 功能

- FastAPI 应用工厂与 `/api/v1/health` 健康检查
- Pydantic Settings 配置管理，支持 `.env` 和环境变量
- SQLAlchemy 2.0 异步数据库层
- Candidate、Job、Interview 数据模型，包含索引、唯一约束和外键约束
- Alembic 数据库迁移配置
- JSON 结构化日志、请求 ID 追踪、请求日志中间件
- CORS、中间件、统一异常处理
- Pytest 单元测试基线

## 本地启动

```bash
cd hiring_agent
cp .env.example .env
poetry install
docker compose up -d postgres redis milvus etcd minio
poetry run alembic upgrade head
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

健康检查：

```bash
curl http://localhost:8000/api/v1/health
```

解析 JD：

```bash
curl -X POST http://localhost:8000/api/v1/jd/parse \
  -H "Content-Type: application/json" \
  -d '{"text":"招聘 Python AI 工程师：985优先，3年以上经验，熟悉 RAG，熟悉 Agent，熟悉 LangChain"}'
```

## 常用命令

```bash
make install
make lint
make typecheck
make test
make migrate
make run
```

## 配置

所有运行时配置都由环境变量或 `.env` 提供。参考 `.env.example`：

- 应用：`APP_NAME`、`APP_ENV`、`APP_DEBUG`、`APP_HOST`、`APP_PORT`、`API_V1_PREFIX`
- 日志：`LOG_LEVEL`、`LOG_JSON`
- CORS：`BACKEND_CORS_ORIGINS`
- 数据库：`DATABASE_URL`、`DATABASE_ECHO`、`DATABASE_POOL_SIZE`、`DATABASE_MAX_OVERFLOW`
- Redis：`REDIS_URL`
- LLM：`LLM_PROVIDER`、`LLM_API_KEY`、`LLM_MODEL`、`LLM_BASE_URL`、`LLM_TIMEOUT_SECONDS`
- Milvus：`MILVUS_HOST`、`MILVUS_PORT`、`MILVUS_USER`、`MILVUS_PASSWORD`、`MILVUS_COLLECTION`
- JD 解析：`JD_PARSER_MODE`、`JD_PARSER_CACHE_TTL_SECONDS`、`JD_PARSER_LLM_MAX_RETRIES`、`JD_PARSER_KNOWN_TECH_STACKS`、`JD_PARSER_BONUS_HINTS`、`JD_PARSER_MUST_HINTS`、`JD_PARSER_EDUCATION_TERMS`、`JD_PARSER_CITY_TERMS`

## 数据库迁移

创建迁移：

```bash
poetry run alembic revision --autogenerate -m "describe change"
```

应用迁移：

```bash
poetry run alembic upgrade head
```

## 测试

```bash
poetry run pytest
```
