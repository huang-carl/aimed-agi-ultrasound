# AIMED Hermes Skills 技能库

## 目录结构

```
skills/
├── aimed/                    # AIMED 项目专属技能
│   ├── README.md             # 本文件
│   ├── diagnostic-report-standard.md    # 标准化诊断报告模板
│   ├── doctor-patient-communication.md  # 医患沟通话术
│   ├── image-analysis-workflow.md       # 超声图像分析标准流程
│   └── compliance-check.md              # 合规边界自动检查
└── README.md                 # 技能库总览
```

## 使用方式

在 Hermes 配置中挂载 skills 目录：

```yaml
# config.yaml
skills:
  external_dirs:
    - /root/.openclaw/workspace/skills
```

## 技能清单

| 技能名称 | 文件 | 描述 | 状态 |
|---------|------|------|------|
| diagnostic-report-standard | diagnostic-report-standard.md | 标准化诊断报告模板（胃/胰腺分型） | 🟡 待完善 |
| doctor-patient-communication | doctor-patient-communication.md | 医患沟通话术（通俗 vs 专业双模式） | 🟡 待完善 |
| image-analysis-workflow | image-analysis-workflow.md | 超声图像分析标准流程 | 🟡 待完善 |
| compliance-check | compliance-check.md | 合规边界自动检查（科研工具 vs 临床诊断） | 🟡 待完善 |

## 维护指南

- 新增技能：在 `aimed/` 目录下创建 `.md` 文件，遵循现有模板
- 更新技能：修改对应文件，更新本 README 的状态列
- 技能命名：使用小写 + 连字符，如 `diagnostic-report-standard`
