# 变更日志 (CHANGELOG)

所有重要的项目变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [0.1.0] - 2026-04-17

### ✨ 新增

- **核心功能**
  - FastAPI 主程序框架
  - 4 个核心 Agent（Conductor、Stomach、Pancreas、Report）
  - 5 个 API 接口（健康检查、胃诊断、胰腺诊断、任务分发、报告生成）
  - 支持 DICOM 和普通图像格式

- **测试**
  - 25 个单元测试用例
  - 测试覆盖率报告支持（pytest-cov）
  - GitHub Actions CI/CD 集成

- **部署**
  - Docker 镜像配置（Dockerfile）
  - Docker Compose 一键部署
  - 健康检查配置

- **文档**
  - README.md（项目说明）
  - DEPLOY.md（部署指南）
  - API.md（接口文档）
  - PROJECT_SUMMARY.md（项目总结）

- **配置**
  - 环境变量模板（.env.example）
  - Git 忽略规则（.gitignore）
  - 依赖管理（requirements.txt）

### 🔧 优化

- 修复 requirements.txt 中 httpx 重复依赖问题
- 添加 MIT LICENSE 开源协议文件
- 完善项目结构和文档

### 📋 技术栈

| 层级 | 技术 |
|------|------|
| Web 框架 | FastAPI 0.109+ |
| Python 版本 | 3.10+ |
| AI 模型 | 阿里云百炼 DashScope |
| 影像处理 | PyDICOM + Pillow |
| 数据库 | SQLite + SQLAlchemy |
| 测试框架 | pytest + pytest-cov |

### ⚠️ 已知限制

- 当前使用 mock 数据，未接入真实 AI 模型
- CORS 配置为允许所有源（生产环境需限制）
- 缺少 API 版本管理（计划 v1.0 添加）

---

## 待发布

### 🎯 计划功能

- [ ] 接入阿里云百炼真实 AI 诊断 API
- [ ] 添加 API 版本管理（/api/v1/）
- [ ] 全局异常处理中间件
- [ ] JWT 认证实现
- [ ] 性能压力测试
- [ ] 更多测试用例（目标 50+）

### 📅 路线图

- **v0.2.0** - AI 模型集成（2026 Q2）
- **v0.3.0** - 性能优化（2026 Q3）
- **v1.0.0** - 生产就绪版本（2026 Q4）

---

**更新频率：** 每次发布新版本时更新

**维护者：** AIMED Agent Swarm 团队
