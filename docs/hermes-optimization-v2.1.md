# Hermes 结构能力优化报告 V2.1

**日期：** 2026-04-26  
**优化人：** 小超同学  
**版本：** 2.0.0 → 2.1.0  

---

## 一、优化前问题清单

| # | 问题 | 严重度 | 影响 |
|---|------|--------|------|
| 1 | 端口不一致 | 🔴 高 | IDENTITY.md 写 18790，config.py 写 18790，实际运行 18792 |
| 2 | Agent 层与 Service 层脱节 | 🔴 高 | ConductorAgent 注册了 Agent，但 main.py 诊断接口直接调 DiagnosisServiceV2，Agent 层未接入 |
| 3 | config.py 未被使用 | 🟡 中 | config.py 定义了完整 Settings，但 main.py 直接用 os.getenv |
| 4 | 路由层重复 | 🟡 中 | main.py 直接定义路由 + routers/v1/ 也有路由，两套实现 |
| 5 | systemd 服务缺失 | 🟡 中 | MEMORY.md 记录已配置，但实际不存在 |
| 6 | model_router.py 未被使用 | 🟡 中 | 有统一路由服务，但 DiagnosisServiceV2 有自己的 fallback 逻辑 |
| 7 | 健康检查信息不足 | 🟢 低 | /health 和 /api/v1/status 缺少 Agent 和路由层信息 |

---

## 二、优化后架构

```
┌─────────────────────────────────────────────────────────┐
│              FastAPI Gateway (main.py)                   │
│  - CORS / 静态文件 / 健康检查 / 系统状态                 │
└────────────────────────┬────────────────────────────────┘
                         │
              ┌──────────┴──────────┐
              │                     │
        routers/v1/            services/
        (路由层 - 6 组)        (服务层 - 12 个)
              │                     │
              │              ┌──────┴──────┐
              │              │             │
              │       model_router    api_key_pool
              │       (统一路由)     (Key 池)
              │              │
              └──────┬───────┘
                     │
              ┌──────┴───────┐
              │              │
         agents/       diagnosis_service_v2
         (智能体层)    (智能降级)
              │
    Conductor → Stomach/Pancreas/Report
```

### 架构分层职责

| 层 | 职责 | 文件 |
|----|------|------|
| **Gateway** | 入口、CORS、静态文件、健康检查 | main.py |
| **Router** | API 路由分发、请求验证 | routers/v1/*.py |
| **Service** | 业务逻辑、AI 调用、数据管理 | services/*.py |
| **Agent** | 专科诊断、任务调度、报告生成 | agents/*.py |
| **Config** | 配置管理、Key 池、模型路由 | config.py / .env |

---

## 三、已完成的优化

### 1. 统一端口 → 18790
- ✅ main.py 默认端口改为 18790
- ✅ 与 IDENTITY.md 和 config.py 保持一致

### 2. Agent 层接入
- ✅ startup_event 中注册所有 Agent 到 Conductor
- ✅ 智能体统计信息加入 /api/v1/status

### 3. 路由层统一
- ✅ 移除 main.py 中的重复路由（/api/v1/diagnose）
- ✅ 通过 app.include_router 挂载 routers/v1/ 的 6 个路由组
- ✅ 保留全局端点（/health, /api/v1/status, /api/v1/segment, /api/v1/knowledge/*）

### 4. 模型路由接入
- ✅ startup_event 中初始化 ModelRouter
- ✅ /api/v1/status 返回模型路由统计
- ✅ /api/v1/models 返回完整提供商信息

### 5. Key 池接入
- ✅ startup_event 中初始化 APIKeyPool
- ✅ /api/v1/status 返回 Key 池状态

### 6. systemd 服务
- ✅ 创建 deploy/hermes.service
- ✅ 配置自动重启、环境变量加载

### 7. 健康检查增强
- ✅ /health 返回 Agent 数量
- ✅ /api/v1/status 返回完整架构信息

---

## 四、待完成的优化

### 高优先级
- [ ] **Conductor 真正调度 Agent**：目前 dispatch_task 是 mock，需要接入真实诊断流程
- [ ] **DiagnosisServiceV2 集成 ModelRouter**：用统一路由替代内置 fallback
- [ ] **config.py 全面接入**：main.py 使用 Settings 替代 os.getenv

### 中优先级
- [ ] **RAG 增强诊断**：诊断前先用 VectorSearch 检索相似病例
- [ ] **图像分割接入诊断流程**：SAM 分割结果作为诊断输入
- [ ] **多语言报告**：ReportAgent 多语言支持完善

### 低优先级
- [ ] **性能监控**：添加 Prometheus 指标
- [ ] **日志优化**：结构化日志 + 日志轮转
- [ ] **API 限流**：防止滥用

---

## 五、性能指标

| 指标 | 优化前 | 优化后 |
|------|--------|--------|
| 架构分层 | 2 层（Gateway + Service） | 4 层（Gateway + Router + Service + Agent） |
| 路由组 | 1 组（main.py 直接定义） | 6 组（routers/v1/） |
| 模型提供商 | 4 个（独立调用） | 4 个（统一路由 + Key 池） |
| Agent 数量 | 4 个（未注册） | 4 个（已注册到 Conductor） |
| 端口一致性 | ❌ 不一致 | ✅ 统一 18790 |
| systemd 服务 | ❌ 缺失 | ✅ 已创建 |

---

## 六、下一步行动

1. **部署验证**：重启 Hermes 服务，验证所有路由正常
2. **Conductor 调度**：实现真正的 Agent 调度逻辑
3. **RAG 诊断**：诊断前检索相似病例，提升准确率
4. **文档更新**：更新 IDENTITY.md 和 MEMORY.md

---

_优化完成时间：2026-04-26 07:05_
