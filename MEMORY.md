# MEMORY.md - 长期记忆

_这是小超同学和小菲同学的共享长期记忆。_

**最后更新：** 2026-04-22

---

## 🧠 核心记忆

### 身份认知
- 双智能体架构：小超同学（钉钉/Hermes 后端）+ 小菲同学（飞书/OpenClaw 前端）
- 共享同一工作空间、配置、数据和 GitHub 仓库
- 职责分离但数据同步

### 项目背景
- **AIMED 充盈视界 FillingVision** - 胃胰超声造影 AI 诊断平台
- 公司：阿尔麦德智慧医疗（湖州）有限公司
- 官网：https://www.aius.xin
- GitHub: https://github.com/huang-carl/aimed-agi-ultrasound
- 愿景：将三甲医院增强造影能力下沉至基层/体检中心

### 技术架构
- **前端：** OpenClaw Gateway (18789 端口) - 钉钉/飞书双渠道
- **后端：** Hermes (18790 端口) - FastAPI + Multi-Agent
- **AI 模型：** 阿里云百炼 (Qwen-Plus) / 本地蒸馏模型
- **数据：** Mock 数据 + 真实医疗数据（小范围演示）

### 已完成工作
- ✅ 2026-04-21：初始化工作空间配置和智能体身份文档
- ✅ 2026-04-21：恢复 GitHub 同步 (`huang-carl/aimed-agi-ultrasound`)
- ✅ 2026-04-21：创建 Demo 演示页面 (`static/demo.html`)
- ✅ 2026-04-21：明确智能体分工（小超-Hermes 后端，小菲-OpenClaw 前端）
- ✅ 2026-04-21：建立自我学习进化机制 (MEMORY.md, LEARNING.md, OPTIMIZATION_PLAN.md)
- ✅ 2026-04-21：Hermes 后端验证和测试框架 (修复 pydantic-settings API, 创建 api_test.py)
- ✅ 2026-04-22：NVIDIA NIM 集成 (Llama-3.3-70B + 双模型路由)
- ✅ 2026-04-22：文物鉴定咨询服务 (乾隆转心瓶 + 汝窑笔洗，北京天鉴文物鉴定有限公司)
- ✅ 2026-04-22：学习 Hermes 多 Agent 最佳实践，创建 `docs/hermes-best-practices.md`

---

## 📚 学习记录

### 技术学习
- **pydantic-settings 2.x API 变更**: `BaseSettings` → `BaseSettingsModel` (2026-04-21)
- **Hermes 后端架构**: FastAPI + Multi-Agent (Conductor + 专科 Agent)
- **API 路由组织**: v1 版本化管理 (`/api/v1/` 前缀)
- **诊断服务设计**: Mock/真实模式切换，支持 DashScope API
- **NVIDIA NIM 集成**: Llama-3.3-70B 验证通过，支持双模型智能路由 (2026-04-22)
- **模型路由策略**: smart(智能)/nvidia/aliyun，长文本>50K 自动用 NVIDIA
- **Hermes 多 Agent 最佳实践**: Profiles + Gateway + Honcho 协同模式，Kimi K2.6 模型推荐 (2026-04-22)

### 用户偏好
- 注重代码质量和文档
- 偏好主动学习和自我进化
- 重视 GitHub 同步和版本管理

### 经验教训
- **依赖版本管理**: pydantic-settings 2.x API 有变更，需要注意版本兼容性
- **测试先行**: 创建 api_test.py 用于快速验证后端状态
- **文档驱动**: OPTIMIZATION_PLAN.md 帮助明确优化方向和优先级

---

## 🎯 待办事项

### 高优先级
- [x] NVIDIA NIM 集成 (2026-04-22 完成)
- [ ] Hermes 后端部署 (18790 端口)
- [ ] GitHub 仓库同步配置
- [ ] 定时任务/提醒设置
- [ ] AIMED 项目相关业务逻辑

### 中优先级
- [ ] 完善 API 文档
- [ ] 添加单元测试
- [ ] 优化错误处理

### 低优先级
- [ ] 性能优化
- [ ] 代码重构
- [ ] 添加更多示例

---

## 📝 重要决策

_记录重要的架构决策、技术选型等_

---

## 🔄 进化日志

| 日期 | 变化 | 说明 |
|------|------|------|
| 2026-04-21 | 初始记忆建立 | 双智能体架构确立 |
| 2026-04-21 | 学习进化机制 | MEMORY.md + LEARNING.md + OPTIMIZATION_PLAN.md |
| 2026-04-21 | Hermes 后端验证 | 修复依赖问题，创建测试框架，24 个 API 路由验证通过 |
| 2026-04-22 | NVIDIA NIM 集成 | Llama-3.3-70B 验证通过，双模型路由机制完成 |
| 2026-04-22 | 心跳机制运行 | 每 30 分钟自动检查系统状态，运行稳定 |
| 2026-04-22 | 新场景探索 | 文物鉴定咨询（非医疗场景），展示多领域适应能力 |

---

_记忆是 curating 的，不是 raw logs。定期回顾和更新。_
