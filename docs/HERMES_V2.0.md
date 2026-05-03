# Hermes V2.0 架构文档

_最后更新：2026-05-03_

---

## 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Gateway (main.py)                 │
│         CORS / 静态文件 / 健康检查 / 路由注册                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
            ┌──────────────┴──────────────┐
            │                             │
     routers/v1/                    services/
     (API 路由层)                   (服务层)
            │                             │
            ├─ diagnosis.py  ───────── diagnosis_service_v2.py
            ├─ stomach.py    ───────── case_database.py
            ├─ pancreas.py   ───────── case_storage.py
            ├─ report.py     ───────── nvidia_service.py
            ├─ conductor.py  ───────── model_router.py
            ├─ cases.py      ───────── blockchain_service.py
            ├─ chat.py       ───────── vector_search.py
            └─ workflow_test.py          ───────── segmentation.py
            │                             │
            └──────────────┬──────────────┘
                           │
            ┌──────────────┴──────────────┐
            │        Agent Swarm           │
            │     (V2.0 架构)              │
            ├──────────────────────────────┤
            │  AgentOrchestrator           │
            │  (工作流编排器)               │
            │    │                         │
            │  MessageBus                  │
            │  (消息总线)                   │
            │    │                         │
            │  ┌─┴─────────────────────┐   │
            │  │                       │   │
            │  │  ConductorAgent       │   │
            │  │  (总指挥/Diagnostic)   │   │
            │  │                       │   │
            │  │  StomachAgent         │   │
            │  │  (胃诊断/Support)      │   │
            │  │                       │   │
            │  │  PancreasAgent        │   │
            │  │  (胰腺诊断/Support)    │   │
            │  │                       │   │
            │  │  ReportAgent          │   │
            │  │  (报告生成/Support)    │   │
            │  └───────────────────────┘   │
            └──────────────────────────────┘
```

---

## V2.0 核心变更

### 1. Agent 基类统一继承

| 基类 | 用途 | 子类 |
|------|------|------|
| `BaseAgent` | 抽象基类，定义 Agent 通用接口 | — |
| `DiagnosticAgent` | 诊断类 Agent（任务调度/分析） | `ConductorAgent` |
| `SupportAgent` | 支撑类 Agent（执行具体任务） | `StomachAgent`, `PancreasAgent`, `ReportAgent` |

### 2. 消息总线 (MessageBus)

- Agent 间通过 `AgentMessage` 通信
- 支持 pub/sub 模式
- 消息类型：`task` / `result` / `error` / `status` / `diagnose` / `generate_report`

### 3. 工作流编排器 (AgentOrchestrator)

- 管理 Agent 注册/注销
- 创建工作流（Agent 序列）
- 执行工作流（依次调用 Agent）
- 任务状态追踪

### 4. API 路由迁移

| 路由 | 迁移状态 | 说明 |
|------|----------|------|
| `diagnosis.py` | ✅ V2.0 | 通过 Agent 处理诊断，支持多模型降级 |
| `stomach.py` | ✅ V2.0 | 直接调用 StomachAgent |
| `pancreas.py` | ✅ V2.0 | 直接调用 PancreasAgent |
| `report.py` | ✅ V2.0 | 直接调用 ReportAgent |
| `conductor.py` | ✅ V2.0 | ConductorAgent 任务管理 |
| `workflow_test.py` | ✅ V2.0 | 工作流测试端点 |
| `cases.py` | ℹ️ 保持 V1 | 数据管理，无需 Agent 架构 |
| `chat.py` | ℹ️ 保持 V1 | 聊天接口，使用 ModelRouter |

---

## Agent 能力矩阵

| Agent | 能力 | 消息类型 |
|-------|------|----------|
| **ConductorAgent** | 任务调度、Agent 协同、结果整合 | `diagnose`, `status` |
| **StomachAgent** | 胃诊断、影像质控、病灶检测 | `diagnose`, `quality_check`, `status` |
| **PancreasAgent** | 胰腺诊断、影像质控、器官分割、风险预测 | `diagnose`, `quality_check`, `segment`, `status` |
| **ReportAgent** | 报告生成、多语言支持、PDF 导出、模板管理 | `generate_report`, `status` |

---

## 降级机制

```
诊断请求 → StomachAgent/PancreasAgent → 成功？
                                          ├─ 是 → 返回 V2.0 结果
                                          └─ 否 → Mock 降级 → 返回 Mock 结果
```

---

## API 端点

### 诊断服务
- `POST /api/v1/diagnosis/diagnose` - AI 诊断（V2.0）
- `GET  /api/v1/diagnosis/models` - 可用模型/Agent 列表

### 胃诊断
- `POST /api/v1/stomach/diagnose` - 胃影像诊断（V2.0）
- `GET  /api/v1/stomach/status` - StomachAgent 状态

### 胰腺诊断
- `POST /api/v1/pancreas/diagnose` - 胰腺影像诊断（V2.0）
- `GET  /api/v1/pancreas/status` - PancreasAgent 状态

### 报告生成
- `POST /api/v1/report/generate` - 生成诊断报告（V2.0）
- `GET  /api/v1/report/status` - ReportAgent 状态

### Conductor
- `POST /api/v1/conductor/dispatch` - 任务分发
- `GET  /api/v1/conductor/task/{id}` - 查询任务状态
- `POST /api/v1/conductor/task/{id}/complete` - 标记完成
- `GET  /api/v1/conductor/stats` - 统计信息

### 工作流测试
- `GET  /api/v1/test/workflows` - 列出工作流
- `POST /api/v1/test/workflow/execute/{name}` - 执行工作流
- `POST /api/v1/test/agent/execute/{id}` - 执行单个 Agent
- `GET  /api/v1/test/orchestrator/stats` - 编排器统计

### 病例管理
- `POST /api/v1/cases/upload` - 上传病例
- `GET  /api/v1/cases/list` - 病例列表
- `GET  /api/v1/cases/{id}` - 病例详情
- `GET  /api/v1/cases/stats/statistics` - 统计信息

### 聊天
- `POST /api/v1/chat` - AI 对话

---

## 技术栈

- **框架：** FastAPI + Uvicorn
- **端口：** 18790
- **Agent 通信：** 异步消息总线
- **模型：** DashScope (qwen3.5-plus/max) + NVIDIA NIM (Llama-3.3-70B)
- **向量检索：** ChromaDB
- **图像分割：** SAM (Segment Anything)
- **区块链：** FISCO BCOS (适配器模式)

---

## 部署

```bash
# systemd 服务
systemctl status hermes

# 重启
systemctl restart hermes

# 日志
journalctl -u hermes -f
```

---

## 下一步

- [ ] Docker Compose 部署验证
- [ ] API 路由迁移完成后的性能测试
- [ ] 真实 AI 模型集成（替代 Mock）
- [ ] 监控和日志系统
- [ ] 单元测试覆盖
