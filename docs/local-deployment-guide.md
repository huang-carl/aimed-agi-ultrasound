# AIMED Agent Swarm 本地部署指南

## 概述

将云端 Agent Swarm（小超同学 + 小菲同学）完整部署到本地电脑。

## 系统要求

| 项目 | 最低要求 | 推荐配置 |
|------|----------|----------|
| OS | macOS 12+ / Ubuntu 20.04+ / Windows 11 | macOS 14+ / Ubuntu 22.04 |
| CPU | 4 核 | 8 核+ |
| 内存 | 8GB | 16GB+ |
| 磁盘 | 50GB | 100GB+ |
| Python | 3.8+ | 3.10+ |
| Node.js | 18+ | 20+ |

## 部署步骤

### 1. 安装 OpenClaw

```bash
# macOS
brew install openclaw

# 或者用 npm
npm install -g openclaw

# 验证安装
openclaw --version
```

### 2. 克隆项目

```bash
# 克隆 GitHub 仓库
cd ~
git clone https://github.com/huang-carl/aimed-agi-ultrasound.git
cd aimed-agi-ultrasound
```

### 3. 安装依赖

```bash
# Python 依赖
pip3 install -r requirements.txt

# 或创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

### 4. 配置环境变量

创建 `.env` 文件：

```bash
# ============================================
# 阿里云百炼 API（主力模型 - Coding Plan）
# ============================================
DASHSCOPE_API_KEY=sk-sp-08e62c85ad194d6f8f05a1dcea27f55a
DASHSCOPE_MODEL=qwen3.5-plus
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# ============================================
# 智谱 AI API（辅助模型 - 永久免费）
# ============================================
ZHIPU_API_KEY=ca0ba668eb3a48558a7f8d81e560172d.evOU5sdde1wTa7c1
ZHIPU_MODEL=glm-4-flash
ZHIPU_BASE_URL=https://open.bigmodel.cn/api/paas/v4/

# ============================================
# DeepSeek API
# ============================================
DEEPSEEK_API_KEY=sk-27b0570804ad43d99fdf67f24a95c502
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# ============================================
# NVIDIA NIM（备用）
# ============================================
NVIDIA_API_KEY=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
NVIDIA_MODEL=meta/llama-3.3-70b-instruct
```

### 5. 配置 OpenClaw

创建 `~/.openclaw/openclaw.json`：

```json
{
  "meta": {
    "lastTouchedVersion": "2026.3.23"
  },
  "models": {
    "mode": "merge",
    "providers": {
      "dashscope": {
        "baseUrl": "https://coding.dashscope.aliyuncs.com/v1",
        "apiKey": "${DASHSCOPE_API_KEY}",
        "api": "openai-completions",
        "models": [
          {
            "id": "qwen3.5-plus",
            "name": "Qwen3.5 Plus",
            "reasoning": true,
            "input": ["text", "image"],
            "contextWindow": 1000000,
            "maxTokens": 65536
          },
          {
            "id": "qwen3-max-2026-01-23",
            "name": "Qwen3 Max Thinking",
            "reasoning": true,
            "contextWindow": 262144,
            "maxTokens": 65536
          },
          {
            "id": "qwen3-coder-plus",
            "name": "Qwen3 Coder Plus",
            "contextWindow": 1000000,
            "maxTokens": 65536
          },
          {
            "id": "kimi-k2.5",
            "name": "Kimi K2.5",
            "reasoning": true,
            "input": ["text", "image"],
            "contextWindow": 262144,
            "maxTokens": 262144
          }
        ]
      }
    }
  },
  "plugins": {
    "entries": {}
  }
}
```

### 6. 启动服务

```bash
# 启动 Hermes 后端
cd ~/aimed-agi-ultrasound
python3 -m uvicorn main:app --host 0.0.0.0 --port 18790

# 启动 OpenClaw Gateway
openclaw gateway start
```

### 7. 验证部署

```bash
# 检查 Hermes
curl http://localhost:18790/api/v1/status

# 检查 OpenClaw
openclaw gateway status
```

## 本地开发工作流

### 代码同步

```bash
# 拉取最新代码
git pull origin main

# 更新依赖
pip3 install -r requirements.txt

# 重启服务
openclaw gateway restart
```

### 本地调试

```bash
# 开发模式（自动重载）
python3 -m uvicorn main:app --reload --port 18790

# 查看日志
tail -f logs/hermes.log
```

## 配置说明

### 端口分配

| 服务 | 端口 | 说明 |
|------|------|------|
| Hermes 后端 | 18790 | FastAPI 诊断服务 |
| OpenClaw Gateway | 18789 | 前端交互网关 |
| 静态文件 | 8080 | Nginx 本地代理 |

### 目录结构

```
~/aimed-agi-ultrasound/
├── main.py              # 主入口
├── config.py            # 配置管理
├── services/            # 服务层
│   ├── diagnosis_service_v2.py
│   ├── blockchain_service.py
│   └── ...
├── routers/             # 路由层
│   └── v1/
├── static/              # 前端静态文件
│   ├── index.html
│   ├── demo.html
│   └── portal/
├── config/              # 配置文件
│   └── blockchain.json
└── docs/                # 文档
```

## 常见问题

### 1. 端口冲突

```bash
# 检查端口占用
lsof -i :18790
lsof -i :18789

# 修改端口
# 编辑 main.py 中的 port 参数
```

### 2. 依赖安装失败

```bash
# 使用国内镜像
pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### 3. 模型调用失败

```bash
# 检查 API Key
cat .env | grep API_KEY

# 测试连接
curl -X POST https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen3.5-plus","messages":[{"role":"user","content":"hello"}]}'
```

## 下一步

1. ✅ 本地部署完成
2. 🔄 同步云端数据
3. 📱 连接钉钉/飞书渠道
4. 🧪 测试诊断功能
5. 🚀 部署到生产环境
