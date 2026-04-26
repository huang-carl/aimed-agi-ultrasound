# 快速开始 (Quick Start)

5 分钟快速启动 AIMED Agent Swarm 服务。

---

## 🚀 方式一：本地开发（推荐新手）

### 1. 克隆仓库

```bash
git clone https://github.com/huang-carl/aimed-agi-ultrasound.git
cd aimed-agi-ultrasound
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置 API Key

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，设置 API Key
# DASHSCOPE_API_KEY=sk-your-actual-key
```

### 5. 启动服务

```bash
python main.py
```

### 6. 访问 API 文档

打开浏览器访问：**http://localhost:8000/docs**

---

## 🐳 方式二：Docker 部署（推荐生产）

### 1. 克隆仓库

```bash
git clone https://github.com/huang-carl/aimed-agi-ultrasound.git
cd aimed-agi-ultrasound
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，设置 DASHSCOPE_API_KEY
```

### 3. 启动 Docker

```bash
cd deploy
docker-compose up -d
```

### 4. 查看日志

```bash
docker-compose logs -f
```

### 5. 健康检查

```bash
curl http://localhost:8000/health
```

---

## 🧪 测试接口

### 使用 curl

```bash
# 健康检查
curl http://localhost:8000/health

# 胃诊断（需准备测试图像）
curl -X POST "http://localhost:8000/api/stomach/diagnose" \
  -F "file=@test_image.png"
```

### 使用 Python

```python
import requests

# 健康检查
response = requests.get("http://localhost:8000/health")
print(response.json())

# 胃诊断
files = {"file": open("test_image.png", "rb")}
response = requests.post(
    "http://localhost:8000/api/stomach/diagnose",
    files=files
)
print(response.json())
```

### 使用 Swagger UI

1. 访问 http://localhost:8000/docs
2. 选择接口（如 `/api/stomach/diagnose`）
3. 点击 "Try it out"
4. 上传测试文件
5. 点击 "Execute"

---

## 🔧 常见问题

### 问题 1：端口被占用

**错误：** `Address already in use`

**解决：**
```bash
# 方式一：修改端口
# 编辑 .env 文件，设置 PORT=8001

# 方式二：查找并关闭占用进程
lsof -i :8000
kill -9 <PID>
```

### 问题 2：依赖安装失败

**错误：** `Could not find a version that satisfies the requirement`

**解决：**
```bash
# 升级 pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题 3：Docker 启动失败

**错误：** `Cannot start service`

**解决：**
```bash
# 检查 Docker 是否运行
docker ps

# 重启 Docker 服务
sudo systemctl restart docker

# 清理并重新构建
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 问题 4：API Key 无效

**错误：** `Invalid API key`

**解决：**
1. 访问 https://dashscope.console.aliyun.com/apiKey
2. 创建或复制 API Key
3. 更新 `.env` 文件中的 `DASHSCOPE_API_KEY`
4. 重启服务

---

## 📚 下一步

- **[API 示例](API_EXAMPLES.md)** - 查看详细接口用法
- **[开发指南](DEVELOPMENT_GUIDE.md)** - 本地开发和调试
- **[部署清单](DEPLOYMENT_CHECKLIST.md)** - 生产环境部署

---

**预计耗时：** 5-10 分钟  
**难度：** ⭐☆☆☆☆
