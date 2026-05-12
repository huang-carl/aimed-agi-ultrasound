# AIMED Agent Swarm - 上消化器官超声造影普筛早查服务生态 v1.0

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)

**充盈视界 FillingVision - 上消化器官超声造影 AI 多智能体诊断平台**

---

## ⚠️ 重要声明

### 1. 系统用途
本系统**仅用于演示和项目说明**，展示 AI 辅助医疗诊断的技术方案、多智能体协作架构设计等内容。**本系统不构成医疗建议，不能替代专业医生的诊断。**

### 2. API Key 安全说明
本项目代码中之前暴露的所有 API Key（包括 NVIDIA API Key 等）**均已作废并更换**。当前代码库中的所有 API Key 仅用于演示配置示例，不包含任何有效的生产环境密钥。实际使用时需通过环境变量配置自己的有效密钥。

### 3. 项目合作
- **临床合作单位**：湖州师范学院附属第一医院
- **项目负责人**：管建明 - 湖州师范学院附属第一医院

---

## 📋 项目概述

本项目依托口服超声造影剂与充盈超声造影检查核心技术，结合深度学习与多智能体 AI 算法，打造专业化上消化道无创智能诊断平台。

### 核心公式

```
AIMED = 三剂 + 一法 + 一服务体系

三剂：胰腺型 + 胃肠型 + 胆管型 口服超声造影剂
一法：标准化充盈超声造影检查流程
一系统：AI 多智能体诊断平台（Hermes）
```

### 核心定位

- **重点识别排序（当前）：** **胃 🥇 | 胰腺 🥈**（双核心优先）
- **后续研发排序：** 胆管 → 食道 → 贲门 → 十二指肠
- **发展策略：** 深耕胃胰双核心，验证成功后按序延伸至其他器官
- **服务场景：** 体检中心普筛、基层医院诊疗、科研合作
- **技术特点：** 无创、无辐射、低成本、可重复检查
- **部署方式：** 轻量化部署，适配各类通用硬件设备
- **合规定位：** Phase 1 科研工具（非临床诊断）

---

## 🎯 器官识别优先级

| 优先级 | 器官 | 状态 | 说明 |
|--------|------|------|------|
| 🥇 **P0** | **胃** | ✅ 已实现 | 最高优先级，AI诊断已接入 |
| 🥈 **P0** | **胰腺** | ✅ 已实现 | 最高优先级，AI诊断已接入 |
| 🥉 **P1** | **胆管** | ⏳ 待启动 | Phase 2 (2027 Q1) |
| **P2** | **食道** | ⏳ 待启动 | Phase 2 (2027 Q2) |
| **P3** | **贲门** | ⏳ 待启动 | Phase 3 (2027 Q3) |
| **P4** | **十二指肠** | ⏳ 待启动 | Phase 3 (2027 Q3) |

---

## 🚀 核心特性

- ✅ **实时超声影像智能处理与病灶精准识别**
- ✅ **无创可视化上消化道器官诊断分析**
- ✅ **多 AI 智能体协同辅助诊断，提升诊断一致性**
- ✅ **轻量化部署，适配各类通用硬件设备**
- ✅ **临床友好型操作界面，流程简洁易上手**
- ✅ **多模型智能路由（DeepSeek / DashScope / 智谱 AI）**

---

## 🏗️ 系统架构

### 多智能体协同

```
┌─────────────────────────────────────────┐
│     Conductor Agent (总指挥)            │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
┌───────────────┐   ┌───────────────┐
│  Stomach      │   │  Pancreas     │
│   Agent       │   │   Agent       │
│  🥇 P0 胃      │   │  🥈 P0 胰腺    │
└───────────────┘   └───────────────┘
```

### 技术栈

| 层级 | 技术选型 |
|------|---------|
| Web 框架 | FastAPI + Uvicorn |
| AI 模型 | DeepSeek / 阿里云百炼 (DashScope) / 智谱 AI |
| 影像处理 | PyDICOM + SimpleITK + Pillow |
| 数据库 | SQLite + SQLAlchemy |
| 认证安全 | Python-JOSE + Passlib |
| 报告生成 | ReportLab + Jinja2 |
| 日志 | Loguru |

---

## 📦 快速开始

### 本地开发

```bash
# 1. 克隆仓库
git clone https://github.com/huang-carl/aimed-agi-ultrasound.git
cd aimed-agi-ultrasound

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 API Key

# 5. 启动服务
python main.py

# 6. 访问 API 文档
# http://localhost:18790/docs
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
  "version": "1.0.0"
}
```

### 胃诊断

```bash
POST /api/v1/stomach/diagnose
Content-Type: multipart/form-data

file: [超声影像文件]
image_description: [影像描述]
```

### 胰腺诊断

```bash
POST /api/v1/pancreas/diagnose
Content-Type: multipart/form-data

file: [超声影像文件]
image_description: [影像描述]
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
├── DEMO_STATEMENT.md            # 演示声明
├── routers/                     # API 路由
│   ├── __init__.py
│   ├── conductor.py             # 总指挥路由
│   ├── stomach.py               # 胃诊断路由
│   ├── pancreas.py              # 胰腺诊断路由
│   ├── report.py                # 报告生成路由
│   └── v1/                      # API v1 版本
├── agents/                      # AI 智能体
│   ├── __init__.py
│   ├── base_agent.py            # Agent 基类
│   ├── conductor_agent.py       # 总指挥 Agent
│   ├── stomach_agent.py         # 胃诊断 Agent
│   ├── pancreas_agent.py        # 胰腺诊断 Agent
│   ├── report_agent.py          # 报告生成 Agent
│   ├── orchestrator.py          # 编排器
│   └── message_bus.py           # 消息总线
├── services/                    # 服务层
│   ├── __init__.py
│   ├── diagnosis_service.py     # 诊断服务
│   ├── diagnosis_service_v2.py  # 诊断服务 V2
│   ├── ai_diagnosis_service.py  # AI诊断服务
│   └── ...
├── middleware/                  # 中间件
├── models/                      # 模型权重
├── data/                        # 数据目录
├── deploy/                      # 部署配置
├── tests/                       # 测试用例
├── docs/                        # 文档目录
└── static/                      # 静态文件
```

---

## 🔐 配置说明

### 环境变量 (.env)

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DASHSCOPE_API_KEY` | 阿里云百炼 API Key | 必填 |
| `ZHIPU_API_KEY` | 智谱 AI API Key | 可选 |
| `DEEPSEEK_API_KEY` | DeepSeek API Key | 可选 |
| `HOST` | 服务监听地址 | `0.0.0.0` |
| `PORT` | 服务端口 | `18790` |
| `DEBUG` | 调试模式 | `true` |
| `MOCK_MODE` | Mock 模式 | `true` |

---

## 📊 性能指标

| 指标 | 状态 |
|------|------|
| 单次诊断响应时间 | < 3s ✅ |
| 系统可用性 | > 99.9% ✅ |
| AI 识别准确率 | 80%+ ✅ |
| 并发支持 | 10+ QPS ✅ |

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

本项目当前为**科研工具**，仅限以下用途：
- ✅ 科研合作（与医院/高校联合课题）
- ✅ 技术验证（内部测试 + Mock 数据）
- ✅ 学术交流（论文/会议/演示）
- ✅ 数据采集（伦理审批 + 患者授权）

**AI 分析结果仅供参考，最终诊断请以执业医师判断为准。**

---

**版本：** v1.0.0  
**更新日期：** 2026-05-12  
**核心定位：** 上消化器官超声造影普筛早查服务生态
