# AIMED Agent Swarm - 胃胰超声造影 AI 诊断系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)

**聚焦胃 + 胰腺 2 器官的充盈超声造影 AI 辅助诊断系统**

---

## 📋 项目概述

本项目依托口服超声造影剂与充盈超声造影检查核心技术，结合深度学习与多智能体 AI 算法，打造专业化上消化道无创智能诊断平台。

### 核心定位

- **聚焦器官：** 胃、胰腺（2 器官首选）
- **服务场景：** 体检中心普筛、基层医院诊疗
- **技术特点：** 无创、低成本、可重复检查
- **部署方式：** 轻量化部署，适配各类通用硬件设备

---

## 🚀 核心特性

- ✅ **实时超声影像智能处理与病灶精准识别**
- ✅ **无创可视化上消化道器官诊断分析**
- ✅ **多 AI 智能体协同辅助诊断，提升诊断一致性**
- ✅ **轻量化部署，适配各类通用硬件设备**
- ✅ **临床友好型操作界面，流程简洁易上手**

---

## 🏗️ 系统架构

### 4 个核心 Agent

```
┌─────────────────────────────────────────┐
│     Conductor Agent (总指挥)            │
│  - 任务调度与路由                        │
│  - 多 Agent 协同                          │
│  - 结果整合                              │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┼─────────┐
        │         │         │
        ▼         ▼         ▼
┌───────────┐ ┌───────────┐ ┌───────────┐
│  Stomach  │ │ Pancreas  │ │  Report   │
│   Agent   │ │   Agent   │ │   Agent   │
│  胃诊断   │ │ 胰腺诊断  │ │ 报告生成  │
└───────────┘ └───────────┘ └───────────┘
```

### 技术栈

| 层级 | 技术选型 |
|------|---------|
| Web 框架 | FastAPI + Uvicorn |
| AI 模型 | 阿里云百炼 (DashScope) |
| 影像处理 | PyDICOM + SimpleITK + Pillow |
| 数据库 | SQLite + SQLAlchemy |
| 认证安全 | Python-JOSE + Passlib |
| 报告生成 | ReportLab + Jinja2 |
| 日志 | Loguru |

---

## 📦 快速开始

### 方式一：本地开发

```bash
# 1. 克隆仓库
git clone https://github.com/huang-carl/aimed-agi-ultrasound.git
cd aimed-agi-ultrasound

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 DASHSCOPE_API_KEY

# 5. 启动服务
python main.py

# 6. 访问 API 文档
# http://localhost:8000/docs
```

### 方式二：Docker 部署

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 DASHSCOPE_API_KEY

# 2. 启动 Docker
cd deploy
docker-compose up -d

# 3. 查看日志
docker-compose logs -f

# 4. 停止服务
docker-compose down
```

---

## 📡 API 接口

### 健康检查

```bash
GET /health
```

**响应示例：**
```json
{
  "status": "ok",
  "service": "AIMED Agent Swarm",
  "version": "0.1.0"
}
```

---

### 胃诊断

```bash
POST /api/stomach/diagnose
Content-Type: multipart/form-data

file: [超声影像文件]
```

**响应示例：**
```json
{
  "organ": "胃",
  "disease": "慢性胃炎",
  "probability": 0.85,
  "suggestion": "建议结合临床症状，必要时行胃镜检查",
  "image_quality": "good",
  "timestamp": "2026-04-17T08:00:00"
}
```

---

### 胰腺诊断

```bash
POST /api/pancreas/diagnose
Content-Type: multipart/form-data

file: [超声影像文件]
```

**响应示例：**
```json
{
  "organ": "胰腺",
  "disease": "胰腺回声均匀",
  "probability": 0.92,
  "suggestion": "未见明显异常，建议定期体检",
  "image_quality": "good",
  "timestamp": "2026-04-17T08:00:00"
}
```

---

### 任务分发（总指挥）

```bash
POST /api/conductor/dispatch
Content-Type: application/json

{
  "organs": ["stomach", "pancreas"],
  "image_paths": ["/path/to/image1.png", "/path/to/image2.png"],
  "patient_id": "PAT001"
}
```

**响应示例：**
```json
{
  "task_id": "task_20260417080000",
  "status": "processing",
  "created_at": "2026-04-17T08:00:00"
}
```

---

### 报告生成

```bash
POST /api/report/generate
Content-Type: application/json

{
  "patient_id": "PAT001",
  "patient_name": "张三",
  "diagnosis_results": [
    {
      "organ": "胃",
      "disease": "慢性胃炎",
      "probability": 0.85,
      "suggestion": "建议结合临床症状"
    }
  ],
  "doctor_id": "DR001",
  "doctor_name": "李医生"
}
```

---

## 🧪 运行测试

```bash
# 安装测试依赖
pip install pytest pytest-asyncio

# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_conductor.py -v

# 生成覆盖率报告
pytest --cov=agents tests/
```

---

## 📁 项目结构

```
aimed-agi-ultrasound/
├── main.py                      # FastAPI 主程序
├── config.py                    # 配置管理
├── requirements.txt             # Python 依赖
├── .env.example                 # 环境变量模板
├── README.md                    # 项目说明
├── routers/                     # API 路由
│   ├── __init__.py
│   ├── conductor.py             # 总指挥路由
│   ├── stomach.py               # 胃诊断路由
│   ├── pancreas.py              # 胰腺诊断路由
│   └── report.py                # 报告生成路由
├── agents/                      # AI 智能体
│   ├── __init__.py
│   ├── conductor_agent.py       # 总指挥 Agent
│   ├── stomach_agent.py         # 胃诊断 Agent
│   ├── pancreas_agent.py        # 胰腺诊断 Agent
│   └── report_agent.py          # 报告生成 Agent
├── models/                      # 模型权重
│   └── .gitkeep
├── data/                        # 数据目录
│   ├── samples/                 # 测试样本
│   └── reports/                 # 生成的报告
├── deploy/                      # 部署配置
│   ├── Dockerfile
│   └── docker-compose.yml
├── tests/                       # 测试用例
│   ├── __init__.py
│   ├── test_conductor.py
│   ├── test_stomach.py
│   ├── test_pancreas.py
│   └── test_report.py
└── logs/                        # 日志目录
    └── .gitkeep
```

---

## 🔐 配置说明

### 环境变量 (.env)

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DASHSCOPE_API_KEY` | 阿里云百炼 API Key | 必填 |
| `HOST` | 服务监听地址 | `0.0.0.0` |
| `PORT` | 服务端口 | `8000` |
| `DEBUG` | 调试模式 | `true` |
| `DATABASE_URL` | 数据库连接 URL | `sqlite+aiosqlite:///./aimed.db` |
| `JWT_SECRET_KEY` | JWT 密钥 | 必填（生产环境） |
| `LOG_LEVEL` | 日志级别 | `INFO` |

---

## 📊 性能指标

| 指标 | 目标值 | 当前状态 |
|------|--------|---------|
| 单次诊断响应时间 | < 3s | ✅ (mock 数据) |
| 系统可用性 | > 99.9% | ⏳ 待测试 |
| AI 识别准确率 | > 90% | ⏳ 待真实模型 |
| 并发支持 | 10+ QPS | ⏳ 待压测 |

---

## 🤝 共建单位

**超声造影人工智能诊断联合实验室/联合实践基地**

- 阿尔麦德智慧医疗（湖州）有限公司
- 南京大学
- 湖州师范学院附属第一医院

---

## 📞 联系方式

- **官网：** https://www.aius.xin
- **邮箱：** aimed@aius.xin
- **GitHub：** https://github.com/huang-carl/aimed-agi-ultrasound

---

## 📄 开源协议

MIT License

---

## ⚠️ 免责声明

本项目仅供科研和技术交流使用，**不得用于临床诊断**。

AI 诊断结果仅供参考，最终诊断请以执业医师判断为准。

---

**版本：** v0.1.0  
**更新日期：** 2026-04-17
