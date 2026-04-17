# 部署检查清单 (Deployment Checklist)

## 📋 部署前检查

### 环境准备

- [ ] 服务器操作系统（Ubuntu 22.04+ 推荐）
- [ ] Python 3.10+ 已安装
- [ ] Git 已安装
- [ ] Docker 和 Docker Compose（如使用容器部署）
- [ ] 域名和 SSL 证书（生产环境）
- [ ] 防火墙规则配置（端口 80/443/8000）

### 代码准备

- [ ] 代码已从 GitHub 克隆
- [ ] 切换到正确的分支（master/release）
- [ ] 运行 `git status` 确认无未提交更改
- [ ] 查看 `CHANGELOG.md` 了解最新版本变更

### 配置检查

- [ ] 复制 `.env.example` 到 `.env`
- [ ] 配置 `DASHSCOPE_API_KEY`（阿里云百炼 API Key）
- [ ] 配置 `JWT_SECRET_KEY`（生产环境必须修改）
- [ ] 设置 `DEBUG=false`（生产环境）
- [ ] 配置 `ALLOWED_ORIGINS`（限制具体域名）
- [ ] 检查数据库连接字符串
- [ ] 确认日志路径可写

### 依赖安装

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 验证安装
pip list | grep fastapi
```

- [ ] 虚拟环境已创建
- [ ] 所有依赖安装成功
- [ ] 无版本冲突警告

---

## 🚀 部署方式

### 方式一：Docker 部署（推荐）

```bash
cd deploy

# 1. 检查配置文件
cat docker-compose.yml

# 2. 构建镜像
docker-compose build

# 3. 启动服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f

# 5. 健康检查
curl http://localhost:8000/health
```

- [ ] Docker 镜像构建成功
- [ ] 容器启动正常
- [ ] 健康检查通过
- [ ] 日志无 ERROR 级别错误

### 方式二：直接部署

```bash
# 1. 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# 2. 后台运行（使用 systemd 或 supervisor）
# 示例：systemd 服务配置
```

- [ ] 服务启动成功
- [ ] 多进程配置（生产环境建议 4+ workers）
- [ ] 进程守护配置（systemd/supervisor）
- [ ] 开机自启动配置

---

## 🔒 安全检查

### 网络安全

- [ ] 防火墙仅开放必要端口（80/443）
- [ ] SSH 使用密钥认证（禁用密码）
- [ ] 失败登录限制（fail2ban）
- [ ] DDoS 防护（如 Cloudflare）

### 应用安全

- [ ] `DEBUG=false`（生产环境）
- [ ] CORS 限制具体域名
- [ ] JWT 密钥已更换（非默认值）
- [ ] API Key 未硬编码在代码中
- [ ] 数据库使用强密码
- [ ] 文件上传大小限制
- [ ] 输入验证启用

### 数据安全

- [ ] 数据库定期备份
- [ ] 备份文件加密存储
- [ ] 敏感数据脱敏
- [ ] 日志不包含敏感信息
- [ ] HTTPS 启用（生产环境）

---

## 📊 监控配置

### 日志监控

```bash
# 查看实时日志
tail -f logs/aimed.log

# 查看错误日志
grep ERROR logs/aimed.log | tail -20

# 日志轮转配置（logrotate）
```

- [ ] 日志文件可写
- [ ] 日志轮转配置（防止磁盘占满）
- [ ] 错误日志告警配置

### 性能监控

- [ ] CPU 使用率监控（阈值：80%）
- [ ] 内存使用率监控（阈值：85%）
- [ ] 磁盘空间监控（阈值：90%）
- [ ] 响应时间监控（P95 < 500ms）
- [ ] 请求量监控

### 健康检查

```bash
# 定时健康检查（cron 或监控工具）
*/5 * * * * curl -f http://localhost:8000/health || echo "Health check failed"
```

- [ ] 健康检查端点可用
- [ ] 自动告警配置
- [ ] 故障恢复流程

---

## 🧪 部署后验证

### 功能测试

```bash
# 1. 健康检查
curl http://localhost:8000/health

# 2. 胃诊断接口
curl -X POST http://localhost:8000/api/stomach/diagnose \
  -F "file=@test_image.png"

# 3. 胰腺诊断接口
curl -X POST http://localhost:8000/api/pancreas/diagnose \
  -F "file=@test_image.png"

# 4. API 文档
open http://localhost:8000/docs
```

- [ ] 健康检查通过
- [ ] 诊断接口响应正常
- [ ] API 文档可访问
- [ ] 响应时间 < 3 秒

### 性能测试

```bash
# 使用 ab 或 wrk 进行压力测试
ab -n 1000 -c 10 http://localhost:8000/health
```

- [ ] 并发 10+ 请求无错误
- [ ] P95 响应时间 < 500ms
- [ ] 无内存泄漏

### 回滚计划

- [ ] 备份当前版本
- [ ] 回滚脚本准备
- [ ] 数据库回滚方案
- [ ] 回滚测试完成

---

## 📝 文档更新

- [ ] 更新部署文档
- [ ] 记录配置变更
- [ ] 更新运维手册
- [ ] 通知相关人员

---

## ✅ 部署完成确认

| 检查项 | 状态 | 负责人 | 日期 |
|--------|------|--------|------|
| 环境准备 | ☐ | | |
| 配置检查 | ☐ | | |
| 安全检查 | ☐ | | |
| 功能测试 | ☐ | | |
| 监控配置 | ☐ | | |
| 文档更新 | ☐ | | |

**部署完成时间：** __________

**部署负责人签字：** __________

---

**版本：** v1.0  
**最后更新：** 2026-04-18
