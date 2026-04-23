# AIMED Agent Swarm - 胃胰超声造影 AI 诊断系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![Test](https://github.com/huang-carl/aimed-agi-ultrasound/actions/workflows/test.yml/badge.svg)](https://github.com/huang-carl/aimed-agi-ultrasound/actions)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**充盈视界 FillingVision - 胃胰超声造影 AI 多智能体诊断平台**

---

## 📋 项目概述

本项目依托口服超声造影剂与充盈超声造影检查核心技术，结合深度学习与多智能体 AI 算法，打造专业化上消化道无创智能诊断平台。

### 核心公式

```
AIMED = 三剂 + 一法 + 一系统

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

### 重点识别排序（Phase 1 - 当前聚焦）

| 优先级 | 器官 | 状态 | 说明 |
|--------|------|------|------|
| 🥇 **P0** | **胃** | 🔥 研发中 | 最高优先级，数据收集 +AI 训练 |
| 🥈 **P0** | **胰腺** | 🔥 研发中 | 最高优先级，数据收集 +AI 训练 |

### 后续研发排序（Phase 2-3）

| 优先级 | 器官 | 状态 | 预计启动 |
|--------|------|------|----------|
| 🥉 **P1** | **胆管** | ⏳ 待启动 | 2027 Q1 |
| **P2** | **食道** | ⏳ 待启动 | 2027 Q2 |
| **P3** | **贲门** | ⏳ 待启动 | 2027 Q3 |
| **P4** | **十二指肠** | ⏳ 待启动 | 2027 Q3 |

---

### 优先级划分依据

**P0（胃 + 胰腺）- 为什么优先？**
1. ✅ **临床需求最大** - 胃癌/胰腺癌发病率高，早筛需求迫切
2. ✅ **技术最成熟** - 充盈超声造影在胃胰应用最广泛
3. ✅ **数据最丰富** - 易于收集标注数据，快速验证 AI 模型
4. ✅ **商业价值最高** - 体检中心普筛首选项目

**P1-P4（胆管/食道/贲门/十二指肠）- 后续延伸**
- 复用胃胰验证的技术架构（造影剂 + 检查流程+AI 诊断）
- 横向复制多智能体模式（每个器官一个专科 Agent）
- 共享数据飞轮和模型训练框架

---

## 🗺️ 战略路线图

| 阶段 | 时间 | 器官聚焦（按优先级） | 核心目标 | 里程碑 | 合规状态 |
|------|------|---------------------|----------|--------|----------|
| **Phase 1** | 2026 Q2-Q4 | 🥇胃 + 🥈胰腺（P0） | 技术验证 + 数据积累 | AI 准确率≥85%<br>500+ 标注病例 | 科研合作模式 |
| **Phase 2** | 2027 Q1-Q3 | 🥉胆管 (P1) + 食道 (P2) | 产品化 + 试点验证 | 10+ 基层医院试点<br>多中心临床试验 | 二类器械备案 |
| **Phase 3** | 2027 Q4+ | 贲门 (P3) + 十二指肠 (P4) | 规模化 + 合规申报 | NMPA 三类证申报<br>50+ 医院商业化 | 三类医疗器械注册证 |

---

## 🚀 核心特性

- ✅ **实时超声影像智能处理与病灶精准识别**
- ✅ **无创可视化上消化道器官诊断分析**
- ✅ **多 AI 智能体协同辅助诊断，提升诊断一致性**
- ✅ **轻量化部署，适配各类通用硬件设备**
- ✅ **临床友好型操作界面，流程简洁易上手**
- ✅ **NVIDIA NIM + 阿里云百炼双模型智能路由**

---

## 🔄 数据飞轮

```
采集 → 标注 → 训练 → 部署 → 反馈 → 再采集
 ↓      ↓      ↓      ↓      ↓       ↓
超声   专科    多智能  云端/   医生    持续    数据
影像   医生    体模型  边缘    修正    迭代    资产
```

**Phase 1 数据目标：** 500+ 标注病例（胃 300+ 胰腺 200+）  
**当前进度：** 18/500 (3.6%)

---

## 🏗️ 系统架构

### 多智能体协同（胃胰双核心 → 六器官全覆盖）

**Phase 1 架构（当前 - P0 优先）：**
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

**Phase 2-3 架构（按序扩展 - P1-P4）：**
```
                  Conductor Agent
                       │
    ┌──────────────────┼──────────────────┐
    │         │        │        │         │
    ▼         ▼        ▼        ▼         ▼
 胃 P0     胰腺 P0   胆管 P1   食道 P2   贲门 P3   十二指肠 P4
 Agent     Agent    Agent    Agent     Agent     Agent
  ✅       ✅        🔄       ⏳        ⏳        ⏳
```

**✅ 当前聚焦：胃 (P0) + 胰腺 (P0)**  
**🔄 后续按序扩展：胆管 (P1) → 食道 (P2) → 贲门 (P3) → 十二指肠 (P4)**

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
│   ├── report.py                # 报告生成路由
│   └── v1/                      # API v1 版本
├── agents/                      # AI 智能体
│   ├── __init__.py
│   ├── conductor_agent.py       # 总指挥 Agent
│   ├── stomach_agent.py         # 胃诊断 Agent
│   ├── pancreas_agent.py        # 胰腺诊断 Agent
│   └── report_agent.py          # 报告生成 Agent
├── middleware/                  # 中间件
│   └── exceptions.py            # 全局异常处理
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
├── docs/                        # 文档目录
│   ├── API_EXAMPLES.md
│   ├── DEPLOYMENT_CHECKLIST.md
│   └── DEVELOPMENT_GUIDE.md
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

### Phase 1（胃 + 胰腺双核心）

| 指标 | 目标值 | 当前状态 |
|------|--------|---------|
| 单次诊断响应时间 | < 3s | ✅ (mock 数据) |
| 系统可用性 | > 99.9% | ⏳ 待测试 |
| AI 识别准确率 | > 85% | ⏳ 待真实模型 |
| 并发支持 | 10+ QPS | ⏳ 待压测 |
| 训练数据规模 | 500+ 病例 | 🔄 18/500 (3.6%) |

### Phase 2-3（按序扩展）

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 器官覆盖 | 6 个 | 胃胰腺 (P0) → 胆管 (P1) → 食道 (P2) → 贲门 (P3) → 十二指肠 (P4) |
| AI 识别准确率 | > 95% | 各器官独立验证 |
| 训练数据规模 | 5000+ 病例 | 六器官合计 |
| NMPA 认证 | 三类证 | 2027 Q4+ 申报 |

---

## 📚 更多文档

### 快速开始
- **[快速开始](docs/QUICKSTART.md)** - 5 分钟快速启动服务 ⭐ 推荐新手
- **[API 示例](docs/API_EXAMPLES.md)** - 详细的 API 使用示例
- **[部署检查清单](docs/DEPLOYMENT_CHECKLIST.md)** - 生产环境部署指南

### 开发参考
- **[开发指南](docs/DEVELOPMENT_GUIDE.md)** - 本地开发和贡献指南
- **[系统架构](docs/ARCHITECTURE.md)** - 技术架构和设计文档
- **[贡献指南](CONTRIBUTING.md)** - 如何参与项目贡献

### 其他
- **[安全策略](SECURITY.md)** - 安全漏洞报告和处理流程
- **[行为准则](CODE_OF_CONDUCT.md)** - 社区行为准则
- **[变更日志](CHANGELOG.md)** - 版本更新记录

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

**Phase 1 合规定边界（2026 Q2-Q4）**

本项目当前为**科研工具**，仅限以下用途：
- ✅ 科研合作（与医院/高校联合课题）
- ✅ 技术验证（内部测试 + Mock 数据）
- ✅ 学术交流（论文/会议/演示）
- ✅ 数据采集（伦理审批 + 患者授权）

**严禁事项：**
- ❌ 对外宣称"诊断"功能（改用"辅助分析"）
- ❌ 直接面向患者提供诊断结论
- ❌ 未经伦理审批收集临床数据
- ❌ 商业化收费（可收成本费/技术服务费）

**重要提示：** AI 分析结果仅供参考，最终诊断请以执业医师判断为准。NMPA 三类医疗器械注册证申报计划于 Phase 3（2027 Q4+）启动。

---

**版本：** v0.2.2  
**更新日期：** 2026-04-23  
**核心逻辑文档：** [docs/aimed-core-logic.md](docs/aimed-core-logic.md)

---

## 💡 核心理念

### 重点识别 · 按序延伸

**从胃 + 胰腺出发，走向六器官全覆盖**

#### 重点识别排序（当前 All-in）
| 优先级 | 器官 | 资源投入 |
|--------|------|----------|
| 🥇 **P0** | **胃** | 100% 研发资源 |
| 🥈 **P0** | **胰腺** | 100% 研发资源 |

#### 后续研发排序（按序启动）
| 优先级 | 器官 | 预计启动 |
|--------|------|----------|
| 🥉 **P1** | **胆管** | Phase 2 (2027 Q1) |
| **P2** | **食道** | Phase 2 (2027 Q2) |
| **P3** | **贲门** | Phase 3 (2027 Q3) |
| **P4** | **十二指肠** | Phase 3 (2027 Q3) |

---

### 底层逻辑公式

```
AIMED = 三剂 + 一法 + 一系统

三剂：胰腺型 + 胃肠型 + 胆管型 口服超声造影剂
一法：标准化充盈超声造影检查流程
一系统：AI 多智能体诊断平台（Hermes）
```

### 发展路径

```
超声先导数据采集
       ↓
  数据大水塘效应（60 例 → 5000 例）
       ↓
  上下兼容其他医疗方法
       ↓
  跨机构/跨部门合作
       ↓
  医疗与人文的数字孪生
       ↓
  智慧城市医疗数字化资产服务生态
```

---

我们选择**胃 + 胰腺**作为起点，因为：
- 🎯 临床需求最迫切（胃癌/胰腺癌高发）
- 🔬 技术最成熟（充盈超声造影应用广泛）
- 📊 数据最丰富（易于收集标注）
- 💰 商业价值最高（体检普筛首选）

验证成功后，我们将**按序横向复制**到胆管→食道→贲门→十二指肠，最终实现：
- ✅ 上消化道六器官全覆盖
- ✅ 统一的 AI 多智能体诊断平台
- ✅ 标准化充盈超声造影检查流程
- ✅ **医疗与人文的数字孪生**
- ✅ **智慧城市医疗数字化资产服务生态**

---

### 生态愿景

| 维度 | 目标 |
|------|------|
| **🏥 医疗** | 疾病诊断、治疗方案、预后评估 |
| **👤 人文** | 患者故事、生活质量、心理状态 |
| **🏙️ 社会** | 区域健康画像、医疗资源优化、公共卫生决策 |

**深耕胃胰，按序延伸，数字孪生，生态共赢。** 🚀
