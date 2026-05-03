# AIMED 双智能体系统 - 迁移指南

**备份时间：** 2026-04-30 22:36  
**备份文件：** `/root/aimed-backup-20260430_223605.tar.gz` (494MB)  
**目标：** 从阿里云服务器 → 本地服务器

---

## 一、当前系统概览

| 组件 | 说明 | 端口 |
|------|------|------|
| **OpenClaw Gateway** | 飞书+钉钉双渠道 | 18789 |
| **Hermes 后端** | FastAPI + Multi-Agent | 18790 |
| **SAM 图像分割** | Segment Anything Model | - |
| **ChromaDB 向量检索** | 23 篇医学文档 | - |
| **Nginx** | 反向代理 + 静态文件 | 80/443 |

### 数据量统计

| 类别 | 大小 | 说明 |
|------|------|------|
| 备份文件 | 494MB | 含工作空间+配置+模型+向量数据 |
| 工作空间 | 157MB | 排除 .venv 和 .git |
| SAM 模型 | 358MB | vit_b 权重 |
| 向量数据 | 15MB | ChromaDB |
| 会话数据 | 42MB | 清理后 |
| 病例数据 | ~15MB | 35+ 张超声图像 |

---

## 二、本地服务器要求

### 最低配置
- CPU: 4 核+
- 内存: 8GB+
- 磁盘: 50GB+
- OS: Ubuntu 22.04 / Debian 12 / CentOS 8+

### 推荐配置
- CPU: 8 核+
- 内存: 16GB+
- 磁盘: 100GB+ SSD
- GPU: NVIDIA GPU（可选，加速图像分割）

---

## 三、迁移步骤

### 步骤 1：下载备份文件

```bash
# 从阿里云服务器下载
scp root@8.141.91.165:/root/aimed-backup-20260430_223605.tar.gz ~/

# 或使用 rsync（支持断点续传）
rsync -avP root@8.141.91.165:/root/aimed-backup-20260430_223605.tar.gz ~/
```

### 步骤 2：安装基础环境

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y nodejs npm python3 python3-pip python3-venv nginx

# CentOS/RHEL
sudo yum install -y nodejs npm python3 python3-pip nginx

# 验证版本
node --version    # 需要 v18+
npm --version     # 需要 v9+
python3 --version # 需要 3.10+
```

### 步骤 3：安装 OpenClaw

```bash
# 全局安装 OpenClaw
npm install -g openclaw

# 验证
openclaw --version
```

### 步骤 4：恢复备份

```bash
# 解压备份
cd ~
tar xzf aimed-backup-20260430_223605.tar.gz

# 恢复 OpenClaw 配置
cp openclaw.json ~/.openclaw/

# 恢复工作空间
cp -r workspace/* ~/.openclaw/workspace/

# 恢复会话数据
cp -r agents/* ~/.openclaw/agents/

# 恢复 SAM 模型
mkdir -p ~/.cache/segment_anything
cp cache/segment_anything/sam_vit_b_01ec64.pth ~/.cache/segment_anything/

# 恢复 systemd 服务（可选）
sudo cp openclaw.service /etc/systemd/system/
sudo cp hermes.service /etc/systemd/system/
```

### 步骤 5：安装 Hermes 依赖

```bash
cd ~/.openclaw/workspace

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装额外依赖
pip install segment-anything torch torchvision chromadb faiss-cpu

# 验证
python3 main.py &
curl http://localhost:18790/api/v1/status
```

### 步骤 6：配置 OpenClaw

```bash
# 编辑配置
nano ~/.openclaw/openclaw.json
```

**需要修改的配置项：**

| 配置项 | 说明 |
|--------|------|
| `channels.feishu` | 飞书应用凭证（保持不变） |
| `channels.clawdbot-dingtalk` | 钉钉应用凭证（保持不变） |
| `gateway.bind` | 改为 `0.0.0.0`（本地访问） |
| `gateway.port` | 18789（保持不变） |

### 步骤 7：配置 Nginx（可选）

```bash
# 复制 Nginx 配置
sudo cp /root/workspace/deploy/nginx.conf /etc/nginx/sites-available/aimed

# 修改域名
sudo nano /etc/nginx/sites-available/aimed
# 将 aius.xin 改为本地域名或 IP

# 启用配置
sudo ln -s /etc/nginx/sites-available/aimed /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 步骤 8：启动服务

```bash
# 启动 OpenClaw
openclaw gateway start

# 启动 Hermes
cd ~/.openclaw/workspace
source .venv/bin/activate
python3 main.py &

# 或使用 systemd
sudo systemctl daemon-reload
sudo systemctl enable openclaw hermes
sudo systemctl start openclaw hermes

# 检查状态
openclaw status
curl http://localhost:18790/api/v1/status
```

---

## 四、验证清单

| 项目 | 命令 | 预期结果 |
|------|------|----------|
| OpenClaw Gateway | `openclaw status` | Gateway running |
| 飞书渠道 | 飞书发消息 | 正常回复 |
| 钉钉渠道 | 钉钉发消息 | 正常回复 |
| Hermes 后端 | `curl localhost:18790/api/v1/status` | 200 OK |
| 诊断 API | `curl localhost:18790/api/v1/diagnosis` | 正常响应 |
| 向量检索 | `curl localhost:18790/api/v1/vector/search` | 23 文档 |
| 图像分割 | `curl localhost:18790/api/v1/segmentation` | SAM 加载 |
| 静态网站 | `curl localhost:18789` | 官网页面 |
| Portal | `curl localhost:18789/portal/` | 登录页面 |

---

## 五、注意事项

### 🔑 凭证安全
- `openclaw.json` 包含飞书/钉钉 API 密钥
- 阿里云 API Key（DashScope）
- NVIDIA API Key
- **迁移后请修改密钥！**

### 🌐 网络配置
- 本地服务器可能需要配置防火墙
- 飞书/钉钉回调地址需要公网可达
- 建议使用 frp/ngrok 做内网穿透

### 📦 .venv 需要重建
- 备份不包含 .venv（5GB Python 依赖）
- 新服务器上需要 `pip install -r requirements.txt` 重建

### 🔄 数据同步
- 迁移后建议设置 Git 同步
- 病例数据、向量数据需要定期备份

---

## 六、可选：Docker 部署

```bash
# 使用 Docker 简化部署
cd ~/.openclaw/workspace/deploy
docker-compose up -d

# 验证
docker ps
curl http://localhost:18789
curl http://localhost:18790/api/v1/status
```

---

## 七、回滚方案

如果本地部署有问题，可以随时切回阿里云：

```bash
# 阿里云服务器保持不变
# 只需修改 DNS/域名解析指向新服务器
# 或直接在飞书/钉钉后台修改回调地址
```

---

## 八、快速命令参考

```bash
# 备份
bash /root/backup-all.sh

# 下载备份
scp root@8.141.91.165:/root/aimed-backup-*.tar.gz ~/

# 启动/停止
openclaw gateway start|stop|restart
systemctl start|stop|restart hermes

# 查看日志
openclaw logs --follow
journalctl -u hermes -f

# 状态检查
openclaw status
curl localhost:18790/api/v1/status
free -h
ps aux --sort=-%mem | head -10
```

---

_迁移指南由小菲同学编制_  
_备份文件位置：`/root/aimed-backup-20260430_223605.tar.gz` (494MB)_
