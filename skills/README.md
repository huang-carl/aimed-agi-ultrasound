# Hermes Skills 技能库总览

## 目录结构

```
skills/
├── README.md                 # 本文件（技能库总览）
└── aimed/                    # AIMED 项目专属技能
    ├── README.md
    ├── diagnostic-report-standard.md    # 标准化诊断报告模板
    ├── doctor-patient-communication.md  # 医患沟通话术
    ├── image-analysis-workflow.md       # 超声图像分析标准流程
    └── compliance-check.md              # 合规边界自动检查
```

## 技能清单

| 分类 | 技能名称 | 描述 | 状态 |
|------|---------|------|------|
| AIMED | diagnostic-report-standard | 标准化诊断报告模板（胃/胰腺分型） | ✅ 已创建 |
| AIMED | doctor-patient-communication | 医患沟通话术（通俗 vs 专业双模式） | ✅ 已创建 |
| AIMED | image-analysis-workflow | 超声图像分析标准流程 | ✅ 已创建 |
| AIMED | compliance-check | 合规边界自动检查（科研工具 vs 临床诊断） | ✅ 已创建 |

## 配置方式

在 Hermes 配置文件中挂载 skills 目录：

```yaml
# ~/.openclaw/config.yaml 或 ~/.hermes/config.yaml
skills:
  external_dirs:
    - /root/.openclaw/workspace/skills
```

## 维护指南

- **新增技能**：在对应分类目录下创建 `.md` 文件
- **更新技能**：修改对应文件，更新本 README 的状态列
- **技能命名**：使用小写 + 连字符，如 `diagnostic-report-standard`
- **文档同步**：每次新增/更新技能后，更新本 README

## 扩展计划

### 待开发技能
- [ ] `data-collection-protocol` - 训练数据采集标准流程
- [ ] `model-evaluation` - AI 模型准确率评估模板
- [ ] `multi-agent-collaboration` - 多 Agent 协同工作流
- [ ] `feedback-loop` - 用户反馈自动沉淀机制

### 通用技能（非 AIMED 专属）
- [ ] `web-research` - 网络调研标准流程
- [ ] `code-review` - 代码审查清单
- [ ] `documentation` - 文档编写规范
