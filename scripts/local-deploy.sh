#!/bin/bash
# ============================================
# AIMED Agent Swarm 本地一键部署脚本
# ============================================

set -e

echo "🚀 开始部署 AIMED Agent Swarm..."

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查 Python
echo -e "${YELLOW}📦 检查 Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 未找到 Python 3，请先安装 Python 3.8+${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python $(python3 --version)${NC}"

# 检查 Node.js
echo -e "${YELLOW}📦 检查 Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠️  未找到 Node.js，OpenClaw 需要 Node.js 18+${NC}"
    echo "   安装命令：brew install node (macOS) 或 apt install nodejs (Ubuntu)"
else
    echo -e "${GREEN}✅ Node $(node --version)${NC}"
fi

# 创建虚拟环境
echo -e "${YELLOW}📦 创建虚拟环境...${NC}"
python3 -m venv .venv
source .venv/bin/activate
echo -e "${GREEN}✅ 虚拟环境已创建${NC}"

# 安装依赖
echo -e "${YELLOW}📦 安装 Python 依赖...${NC}"
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
echo -e "${GREEN}✅ 依赖安装完成${NC}"

# 安装 OpenClaw
echo -e "${YELLOW}📦 安装 OpenClaw...${NC}"
if ! command -v openclaw &> /dev/null; then
    npm install -g openclaw
    echo -e "${GREEN}✅ OpenClaw 已安装${NC}"
else
    echo -e "${GREEN}✅ OpenClaw 已存在${NC}"
fi

# 创建 .env 文件
echo -e "${YELLOW}⚙️  创建 .env 配置...${NC}"
if [ ! -f .env ]; then
    cat > .env << 'EOF'
# ============================================
# 阿里云百炼 API（主力模型 - Coding Plan）
# ============================================
DASHSCOPE_API_KEY=your_api_key_here
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
EOF
    echo -e "${GREEN}✅ .env 已创建${NC}"
else
    echo -e "${GREEN}✅ .env 已存在${NC}"
fi

# 创建数据目录
echo -e "${YELLOW}📁 创建数据目录...${NC}"
mkdir -p data/vectors/medical
mkdir -p logs
echo -e "${GREEN}✅ 目录已创建${NC}"

# 启动服务
echo -e "${YELLOW}🚀 启动服务...${NC}"

# 启动 Hermes 后端
echo -e "${YELLOW}📡 启动 Hermes 后端 (18790)...${NC}"
python3 -m uvicorn main:app --host 0.0.0.0 --port 18790 &
HERMES_PID=$!
echo -e "${GREEN}✅ Hermes 已启动 (PID: $HERMES_PID)${NC}"

# 等待启动
sleep 5

# 验证 Hermes
echo -e "${YELLOW}🔍 验证 Hermes...${NC}"
if curl -s http://localhost:18790/api/v1/status > /dev/null; then
    echo -e "${GREEN}✅ Hermes 运行正常${NC}"
else
    echo -e "${RED}❌ Hermes 启动失败，请查看日志${NC}"
    exit 1
fi

# 启动 OpenClaw Gateway
echo -e "${YELLOW}📡 启动 OpenClaw Gateway (18789)...${NC}"
openclaw gateway start
echo -e "${GREEN}✅ OpenClaw Gateway 已启动${NC}"

# 完成
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}✅ 部署完成！${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "📡 服务地址："
echo "   - Hermes 后端：http://localhost:18790"
echo "   - OpenClaw 前端：http://localhost:18789"
echo ""
echo "🌐 网站页面："
echo "   - 官网：http://localhost:18789/static/index.html"
echo "   - 演示：http://localhost:18789/static/demo.html"
echo "   - 登录：http://localhost:18789/static/portal/login.html"
echo ""
echo "📱 钉钉/飞书渠道："
echo "   - 需要配置 webhook 或机器人"
echo ""
echo "🛑 停止服务："
echo "   kill $HERMES_PID"
echo "   openclaw gateway stop"
echo ""
echo -e "${GREEN}祝使用愉快！${NC}"
