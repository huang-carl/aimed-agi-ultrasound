# AIMED 充盈视界 - 知识库专业分类

**最后更新：** 2026-04-27  
**文档总数：** 36 + 医疗指南  
**分类体系：** 6 大专业领域

---

## 📚 分类体系

### 一、🏥 医疗临床知识 (Medical/Clinical)
*超声造影诊断标准、临床指南、医疗规范*

| 文档 | 说明 |
|------|------|
| [aimed-core-logic.md](aimed-core-logic.md) | AIMED 核心逻辑架构（三剂一法一系统） |
| [ALGORITHM_V1.0.md](ALGORITHM_V1.0.md) | 算法 V1.0 定义（诊断算法/性能指标） |
| [SYSTEM_V1.0.md](SYSTEM_V1.0.md) | 系统 V1.0 定义（核心能力/合规边界） |
| [FRONTEND_V1.0.md](FRONTEND_V1.0.md) | 网站前端 V1.0 定义（页面结构/设计规范） |
| [model-analysis.md](model-analysis.md) | 模型分析文档 |
| [病例管理系统.md](病例管理系统.md) | 病例管理系统设计 |
| [训练数据整理报告.md](训练数据整理报告.md) | 训练数据收集与整理 |

**知识来源：**
- 《胃癌超声初筛临床应用中国专家共识意见（2025 年版）》
- 北京协和医院胰腺囊性病变超声造影研究
- 管建明修订稿 - 胰腺超声造影诊断检查标准

---

### 二、🤖 AI 与算法 (AI/Algorithm)
*多智能体架构、模型路由、向量检索、图像分割*

| 文档 | 说明 |
|------|------|
| [hermes-best-practices.md](hermes-best-practices.md) | Hermes 多 Agent 最佳实践 |
| [hermes-optimization-v2.1.md](hermes-optimization-v2.1.md) | Hermes 结构能力优化 V2.1 |
| [hermes-skills-review.md](hermes-skills-review.md) | Hermes 技能库核查 |
| [multi-model-routing.md](multi-model-routing.md) | 多模型路由机制 |
| [NVIDIA_INTEGRATION.md](NVIDIA_INTEGRATION.md) | NVIDIA NIM 集成文档 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 系统架构设计 |

**技术栈：**
- 阿里云百炼（qwen3.5-plus/coder-plus/max + kimi-k2.5）
- NVIDIA NIM（Llama-3.3-70B）
- SAM 图像分割（ViT-B）
- ChromaDB 向量检索

---

### 三、💻 开发与 API (Development/API)
*API 文档、开发指南、集成示例*

| 文档 | 说明 |
|------|------|
| [API_EXAMPLES.md](API_EXAMPLES.md) | API 调用示例 |
| [HERMES_API_INTEGRATION.md](HERMES_API_INTEGRATION.md) | Hermes API 集成指南 |
| [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) | 开发指南 |
| [QUICKSTART.md](QUICKSTART.md) | 快速入门 |
| [快速入门.md](快速入门.md) | 快速入门（中文版） |
| [小超同学.md](小超同学.md) | 小超同学智能体文档 |

---

### 四、🌐 网站与前端 (Website/Frontend)
*官网设计、演示页面、平台界面*

| 文档 | 说明 |
|------|------|
| [website-architecture.md](website-architecture.md) | 网站架构设计 |
| [网站结构图.md](网站结构图.md) | 网站结构图 |
| [官网设计框架.md](官网设计框架.md) | 官网设计框架 |
| [官网部署指南.md](官网部署指南.md) | 官网部署指南 |
| [官网重构设计 V3.md](官网重构设计 V3.md) | 官网重构设计 V3 |
| [完整内容整合方案.md](完整内容整合方案.md) | 完整内容整合方案 |
| [FRONTEND_V1.0.md](FRONTEND_V1.0.md) | 网站前端 V1.0 定义 |

---

### 五、🚀 部署与运维 (Deployment/Ops)
*部署清单、SSL 配置、访问验证*

| 文档 | 说明 |
|------|------|
| [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) | 部署检查清单 |
| [生产环境部署清单.md](生产环境部署清单.md) | 生产环境部署清单 |
| [SSL 证书配置指南.md](SSL 证书配置指南.md) | SSL 证书配置指南 |
| [部署完成报告.md](部署完成报告.md) | 部署完成报告 |
| [部署状态报告.md](部署状态报告.md) | 部署状态报告 |
| [访问修复报告.md](访问修复报告.md) | 访问修复报告 |
| [公网访问验证报告.md](公网访问验证报告.md) | 公网访问验证报告 |
| [系统集成报告.md](系统集成报告.md) | 系统集成报告 |

---

### 六、📊 战略与展示 (Strategy/Presentation)
*战略规划、答辩材料、区块链资产*

| 文档 | 说明 |
|------|------|
| [答辩核心要点.md](答辩核心要点.md) | 答辩核心要点 |
| [blockchain-digital-assets.md](blockchain-digital-assets.md) | 区块链身份与数字资产 |
| [portal-phase1-report.md](portal-phase1-report.md) | Portal Phase 1 报告 |

---

## 🗂️ 目录结构

```
docs/
├── README.md                    ← 本文件（分类索引）
├── aimed-core-logic.md          ← 医疗临床
├── ALGORITHM_V1.0.md            ← 医疗临床
├── SYSTEM_V1.0.md               ← 医疗临床
├── FRONTEND_V1.0.md             ← 网站前端
├── model-analysis.md            ← 医疗临床
├── 病例管理系统.md              ← 医疗临床
├── 训练数据整理报告.md          ← 医疗临床
├── hermes-best-practices.md     ← AI 与算法
├── hermes-optimization-v2.1.md  ← AI 与算法
├── hermes-skills-review.md      ← AI 与算法
├── multi-model-routing.md       ← AI 与算法
├── NVIDIA_INTEGRATION.md        ← AI 与算法
├── ARCHITECTURE.md              ← AI 与算法
├── API_EXAMPLES.md              ← 开发与 API
├── HERMES_API_INTEGRATION.md    ← 开发与 API
├── DEVELOPMENT_GUIDE.md         ← 开发与 API
├── QUICKSTART.md                ← 开发与 API
├── 快速入门.md                  ← 开发与 API
├── 小超同学.md                  ← 开发与 API
├── website-architecture.md      ← 网站前端
├── 网站结构图.md                ← 网站前端
├── 官网设计框架.md              ← 网站前端
├── 官网部署指南.md              ← 网站前端
├── 官网重构设计 V3.md           ← 网站前端
├── 完整内容整合方案.md          ← 网站前端
├── DEPLOYMENT_CHECKLIST.md      ← 部署与运维
├── 生产环境部署清单.md          ← 部署与运维
├── SSL 证书配置指南.md          ← 部署与运维
├── 部署完成报告.md              ← 部署与运维
├── 部署状态报告.md              ← 部署与运维
├── 访问修复报告.md              ← 部署与运维
├── 公网访问验证报告.md          ← 部署与运维
├── 系统集成报告.md              ← 部署与运维
├── 答辩核心要点.md              ← 战略与展示
├── blockchain-digital-assets.md ← 战略与展示
└── portal-phase1-report.md      ← 战略与展示
```

---

## 📊 统计信息

| 分类 | 文档数 | 占比 |
|------|--------|------|
| 🏥 医疗临床 | 7 | 19% |
| 🤖 AI 与算法 | 6 | 17% |
| 💻 开发与 API | 6 | 17% |
| 🌐 网站前端 | 7 | 19% |
| 🚀 部署与运维 | 8 | 22% |
| 📊 战略与展示 | 3 | 8% |
| **总计** | **37** | **100%** |

---

## 🔍 检索指南

### 按角色查找
| 角色 | 推荐文档 |
|------|----------|
| **医生/临床** | aimed-core-logic.md, ALGORITHM_V1.0.md, SYSTEM_V1.0.md |
| **开发者** | API_EXAMPLES.md, DEVELOPMENT_GUIDE.md, QUICKSTART.md |
| **运维** | DEPLOYMENT_CHECKLIST.md, SSL 证书配置指南.md |
| **产品经理** | FRONTEND_V1.0.md, 官网设计框架.md, 答辩核心要点.md |
| **投资人** | aimed-core-logic.md, 答辩核心要点.md, blockchain-digital-assets.md |

### 按任务查找
| 任务 | 推荐文档 |
|------|----------|
| 了解项目 | aimed-core-logic.md, SYSTEM_V1.0.md |
| 接入 API | API_EXAMPLES.md, HERMES_API_INTEGRATION.md |
| 部署系统 | DEPLOYMENT_CHECKLIST.md, 生产环境部署清单.md |
| 优化算法 | hermes-best-practices.md, multi-model-routing.md |
| 设计界面 | FRONTEND_V1.0.md, 官网设计框架.md |

---

**知识库持续更新中...** 📚
