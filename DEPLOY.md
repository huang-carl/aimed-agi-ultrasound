# AIMED Agent Swarm 部署指南

## 部署方式

### 方式一：本地开发部署

适用于开发和测试环境。

```bash
# 1. 克隆仓库
git clone https://github.com/huang-carl/aimed-agi-ultrasound.git
cd aimed-agi-ultrasound

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入以下关键配置：
# - DASHSCOPE_API_KEY=your_api_key
# - JWT_SECRET_KEY=your_secret_key

# 5. 启动服务
python main.py

# 6. 验证服务
curl http://localhost:8000/health
```

---

### 方式二：Docker 部署（推荐生产环境）

适用于生产环境和服务器部署。

```bash
# 1. 克隆仓库
git clone https://github.com/huang-carl/aimed-agi-ultrasound.git
cd aimed-agi-ultrasound

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入关键配置

# 3. 启动 Docker
cd deploy
docker-compose up -d

# 4. 查看日志
docker-compose logs -f

# 5. 验证服务
curl http://localhost:8000/health

# 6. 停止服务
docker-compose down
```

---

### 方式三：ECS 云服务器部署

适用于阿里云 ECS 等云服务器。

#### 前置要求

- 云服务器：2 核 4GB 以上
- 操作系统：Ubuntu 20.04+ / CentOS 7+
- 开放端口：8000（或自定义）
- 域名（可选）：用于 HTTPS 访问

#### 部署步骤

```bash
# 1. 安装 Docker
curl -fsSL https://get.docker.com | sh

# 2. 安装 Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 3. 克隆项目
git clone https://github.com/huang-carl/aimed-agi-ultrasound.git
cd aimed-agi-ultrasound

# 4. 配置环境变量
cp .env.example .env
vim .env  # 编辑配置

# 5. 启动服务
cd deploy
docker-compose up -d

# 6. 配置防火墙（阿里云安全组）
# 开放 TCP 8000 端口

# 7. 验证服务
curl http://localhost:8000/health
```

---

## 配置说明

### .env 环境变量

| 变量名 | 说明 | 默认值 | 生产建议 |
|--------|------|--------|---------|
| `DASHSCOPE_API_KEY` | 阿里云百炼 API Key | 必填 | 从阿里云控制台获取 |
| `HOST` | 服务监听地址 | `0.0.0.0` | 保持默认 |
| `PORT` | 服务端口 | `8000` | 可自定义 |
| `DEBUG` | 调试模式 | `true` | 生产设为 `false` |
| `DATABASE_URL` | 数据库连接 | SQLite | 生产可用 PostgreSQL |
| `JWT_SECRET_KEY` | JWT 密钥 | 必填 | 使用强随机字符串 |
| `LOG_LEVEL` | 日志级别 | `INFO` | 生产可用 `WARNING` |

---

## 健康检查

```bash
# 基础健康检查
curl http://localhost:8000/health

# 详细健康检查（含服务状态）
curl http://localhost:8000/api/conductor/health
curl http://localhost:8000/api/stomach/health
curl http://localhost:8000/api/pancreas/health
curl http://localhost:8000/api/report/health
```

**预期响应：**
```json
{
  "status": "ok",
  "service": "AIMED Agent Swarm",
  "version": "0.1.0"
}
```

---

## 日志管理

### 查看日志

```bash
# Docker 方式
docker-compose logs -f

# 直接查看日志文件
tail -f logs/aimed.log
```

### 日志级别

- `DEBUG` - 调试信息（开发环境）
- `INFO` - 一般信息（默认）
- `WARNING` - 警告信息
- `ERROR` - 错误信息
- `CRITICAL` - 严重错误

### 日志轮转（生产环境）

建议使用 `logrotate` 配置日志轮转：

```bash
# /etc/logrotate.d/aimed
/var/log/aimed/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0640 root root
}
```

---

## 性能优化

### 生产环境建议

1. **使用 Gunicorn + Uvicorn**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
   ```

2. **启用 HTTPS**
   - 使用 Nginx 反向代理
   - 配置 SSL 证书（Let's Encrypt 免费）

3. **数据库优化**
   - 生产环境使用 PostgreSQL
   - 配置数据库连接池

4. **缓存优化**
   - 使用 Redis 缓存诊断结果
   - 配置适当的缓存过期时间

---

## 故障排查

### 常见问题

**1. 服务无法启动**
```bash
# 检查端口占用
lsof -i :8000

# 检查日志
tail -f logs/aimed.log
```

**2. 依赖安装失败**
```bash
# 升级 pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**3. Docker 启动失败**
```bash
# 查看 Docker 日志
docker-compose logs

# 检查 Docker 状态
docker info
```

---

## 备份与恢复

### 数据备份

```bash
# 备份数据库
cp data/aimed.db data/aimed.db.backup.$(date +%Y%m%d)

# 备份报告
tar -czf reports.backup.$(date +%Y%m%d).tar.gz data/reports/

# 备份日志
tar -czf logs.backup.$(date +%Y%m%d).tar.gz logs/
```

### 数据恢复

```bash
# 恢复数据库
cp data/aimed.db.backup.20260417 data/aimed.db

# 恢复报告
tar -xzf reports.backup.20260417.tar.gz
```

---

## 安全建议

1. **API Key 管理**
   - 不要将 `.env` 文件提交到 Git
   - 定期轮换 API Key

2. **访问控制**
   - 配置防火墙规则
   - 使用 JWT 认证

3. **数据加密**
   - 患者数据加密存储
   - 使用 HTTPS 传输

4. **定期更新**
   - 及时更新依赖包
   - 关注安全漏洞公告

---

**更新日期：** 2026-04-17  
**版本：** v0.1.0
