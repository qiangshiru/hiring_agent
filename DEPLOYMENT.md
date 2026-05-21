# 部署指南

## 目录
1. [环境要求](#环境要求)
2. [本地开发](#本地开发)
3. [Docker 部署](#docker-部署)
4. [Kubernetes 部署](#kubernetes-部署)
5. [云平台部署](#云平台部署)
6. [监控与日志](#监控与日志)
7. [故障排除](#故障排除)

## 环境要求

### 基础环境
- Python 3.11+
- Node.js 18+
- Docker 20.10+
- Docker Compose 2.0+

### 硬件要求
- CPU: 2 核以上
- 内存: 4GB 以上
- 磁盘: 20GB 以上

## 本地开发

### 1. 克隆代码
```bash
git clone https://github.com/your-org/hiring-copilot.git
cd hiring-copilot
```

### 2. 设置后端
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 运行后端
uvicorn src.api.main:app --reload --port 8000
```

### 3. 设置前端
```bash
cd frontend
npm install
npm run dev
```

### 4. 访问应用
- 前端: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

## Docker 部署

### 快速启动
```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 仅启动后端
```bash
docker build -t hiring-agent-api .
docker run -p 8000:8000 hiring-agent-api
```

### 环境变量配置
创建 `.env` 文件：
```env
PYTHONUNBUFFERED=1
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
```

## Kubernetes 部署

### 前置要求
- Kubernetes 1.20+
- kubectl 配置完成
- Ingress 控制器

### 部署步骤
```bash
# 创建命名空间
kubectl create namespace hiring-agent

# 部署后端
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml

# 部署前端
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml

# 部署 Ingress
kubectl apply -f k8s/ingress.yaml

# 检查部署状态
kubectl get pods -n hiring-agent
```

## 云平台部署

### AWS (使用 ECS)
```bash
# 构建 Docker 镜像
docker build -t hiring-agent .

# 推送到 ECR
aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_REGISTRY
docker tag hiring-agent:latest $ECR_REGISTRY/hiring-agent:latest
docker push $ECR_REGISTRY/hiring-agent:latest

# 创建 ECS 任务定义并运行
aws ecs create-task-definition --cli-input-json file://ecs-task-definition.json
aws ecs update-service --cluster hiring-cluster --service hiring-agent --desired-count 2
```

### 阿里云 (使用 ACK)
```bash
# 构建并推送镜像
docker build -t hiring-agent .
docker tag hiring-agent:latest registry.cn-hangzhou.aliyuncs.com/your-namespace/hiring-agent:latest
docker push registry.cn-hangzhou.aliyuncs.com/your-namespace/hiring-agent:latest

# 部署到 ACK
kubectl apply -f k8s/
```

## 监控与日志

### 日志配置
```yaml
# logging.yaml
version: 1
formatters:
  default:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
handlers:
  console:
    class: logging.StreamHandler
  file:
    class: logging.handlers.RotatingFileHandler
    filename: logs/app.log
    maxBytes: 10485760
    backupCount: 5
root:
  level: INFO
  handlers: [console, file]
```

### 监控指标
- 请求延迟
- 错误率
- 吞吐量
- 资源使用率

## 故障排除

### 常见问题

#### 1. 后端启动失败
```bash
# 检查 Python 版本
python --version

# 重新安装依赖
pip install -r requirements.txt --force-reinstall

# 检查端口占用
lsof -i :8000
```

#### 2. 前端构建失败
```bash
# 清除缓存
rm -rf node_modules .next
npm install
npm run build
```

#### 3. Docker 容器无法启动
```bash
# 查看容器日志
docker-compose logs api

# 重建容器
docker-compose down
docker-compose up -d --force-recreate
```

#### 4. 数据库连接失败
```bash
# 检查环境变量
echo $DATABASE_URL

# 测试连接
python -c "from src.db import get_db; next(get_db())"
```

## 安全配置

### 生产环境检查清单
- [ ] 使用 HTTPS
- [ ] 配置 CORS
- [ ] 设置环境变量
- [ ] 启用日志记录
- [ ] 配置备份策略
- [ ] 设置监控告警

### 环境变量示例
```env
# 生产环境
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379
LOG_LEVEL=WARNING
```

## 性能优化

### 后端优化
- 使用 Gunicorn + Uvicorn workers
- 启用 Redis 缓存
- 配置数据库连接池

### 前端优化
- 启用静态资源压缩
- 使用 CDN
- 配置浏览器缓存

## 备份与恢复

### 数据库备份
```bash
# PostgreSQL
pg_dump -U user -d dbname > backup.sql

# MySQL
mysqldump -u user -p dbname > backup.sql
```

### 数据恢复
```bash
psql -U user -d dbname < backup.sql
```
