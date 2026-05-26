# Hiring Agent

企业级 AI 招聘系统，基于 FastAPI + Next.js 构建，支持 JD 解析、简历筛选、面试评价、多 Agent 协同评审等完整招聘流程。

## 系统架构

```
┌─────────────────┐      ┌─────────────────┐
│   Frontend       │      │   API Backend    │
│   Next.js 14     │─────▶│   FastAPI        │
│   :3000          │      │   :8000          │
└─────────────────┘      └────────┬─────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
              PostgreSQL      Redis         Milvus
                (数据)        (缓存)        (向量)
```

## 快速启动 (Docker Compose)

### 前置条件

- Docker & Docker Compose
- 配置好 `.env` 文件中的 `LLM_API_KEY`（如 OpenAI API Key）

### 步骤

```bash
# 1. 克隆并进入项目
cd hiring_agent

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 LLM_API_KEY 等必要配置

# 3. 一键启动所有服务
docker compose up -d
```

服务启动后：
- **前端界面**：http://localhost:3000
- **API 文档**：http://localhost:8000/docs
- **健康检查**：http://localhost:8000/api/v1/health

```bash
# 查看日志
docker compose logs -f

# 停止服务
docker compose down
```

### 基础设施依赖

API 依赖 PostgreSQL、Redis 和 Milvus。当前 docker-compose 仅包含 API 和前端服务，基础设施服务需要额外运行：

```bash
# 使用 Docker 启动基础设施（推荐）
docker run -d --name postgres-hiring \
  -e POSTGRES_USER=hiring_agent \
  -e POSTGRES_PASSWORD=hiring_agent \
  -e POSTGRES_DB=hiring_agent \
  -p 5432:5432 postgres:16

docker run -d --name redis-hiring \
  -p 6379:6379 redis:7
```

> 注意：`.env` 中的服务地址默认为 `localhost`，本地开发时可直接使用。如需全部容器化，可将基础设施加入 docker-compose。

## 本地开发

### 后端

```bash
# 安装依赖
poetry install

# 数据库迁移
poetry run alembic upgrade head

# 启动开发服务器（热重载）
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器（热重载）
npm run dev
```

前端开发服务器运行在 http://localhost:3000，默认通过 `http://localhost:8000` 调用 API。

### Make 命令

```bash
make install      # 安装后端依赖
make run          # 启动后端开发服务器
make test         # 运行测试
make lint         # 代码检查
make typecheck    # 类型检查
make migrate      # 应用数据库迁移
make revision     # 创建新的数据库迁移
make docker-up    # docker compose up -d
make docker-down  # docker compose down
```

## 配置

所有运行时配置通过 `.env` 或环境变量提供。核心配置项：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `LLM_API_KEY` | LLM 服务的 API Key | `replace-me`（**必填**） |
| `LLM_PROVIDER` | LLM 提供商 | `openai` |
| `LLM_MODEL` | 模型名称 | `gpt-4o-mini` |
| `DATABASE_URL` | PostgreSQL 连接串 | `postgresql+asyncpg://...` |
| `REDIS_URL` | Redis 连接串 | `redis://localhost:6379/0` |
| `MILVUS_HOST` | Milvus 主机地址 | `localhost` |

参考 `.env.example` 获取完整配置项。

## 项目结构

```
├── src/                  # 后端源码
│   ├── main.py           # FastAPI 应用入口
│   ├── config.py         # 配置管理
│   ├── database.py       # 数据库连接
│   ├── models/           # 数据模型
│   ├── api/              # API 路由
│   ├── services/         # 业务逻辑
│   └── agents/           # AI Agent 实现
├── frontend/             # 前端源码 (Next.js)
│   └── src/
│       ├── pages/        # 页面组件
│       ├── components/   # UI 组件
│       └── types/        # 类型定义
├── tests/                # 后端测试
├── Dockerfile            # API Dockerfile
├── docker-compose.yml    # Docker Compose
└── .env                  # 环境变量配置
```

## API 示例

```bash
# 健康检查
curl http://localhost:8000/api/v1/health

# 解析 JD
curl -X POST http://localhost:8000/api/v1/jd/parse \
  -H "Content-Type: application/json" \
  -d '{"text":"招聘 Python AI 工程师：985优先，3年以上经验，熟悉 RAG，熟悉 Agent，熟悉 LangChain"}'
```

完整 API 文档请访问 http://localhost:8000/docs。
