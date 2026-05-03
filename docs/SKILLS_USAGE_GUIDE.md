# AIMED Hermes Skills 使用指南

## 快速开始

### 1. 技能库位置
```
/root/.openclaw/workspace/skills/
├── README.md                 # 技能库总览
└── aimed/                    # AIMED 专属技能
    ├── diagnostic-report-standard.md
    ├── doctor-patient-communication.md
    ├── image-analysis-workflow.md
    └── compliance-check.md
```

### 2. 配置挂载
在 Hermes 配置文件中添加 skills 路径：

```yaml
# ~/.openclaw/config.yaml
skills:
  external_dirs:
    - /root/.openclaw/workspace/skills
```

### 3. 验证安装
```bash
cd /root/.openclaw/workspace
python scripts/test_skills.py
```

## 技能使用示例

### 示例 1：生成标准化诊断报告

**触发词：** "生成诊断报告"、"输出报告"、"report"

```python
# API 调用
POST /api/v1/diagnosis
{
    "image": "path/to/ultrasound.jpg",
    "region": "stomach",
    "format": "markdown"  # 自动使用 diagnostic-report-standard 模板
}
```

**输出：** 符合 V1.0 标准的结构化报告，包含：
- 基础信息
- 图像分析结果
- AI 诊断建议
- 免责声明

### 示例 2：医患沟通

**触发词：** "解释给患者"、"通俗说法"、"沟通话术"

```python
# 自动检测对话对象
if user_type == "patient":
    mode = "通俗模式"  # 使用 doctor-patient-communication 通俗版
elif user_type == "doctor":
    mode = "专业模式"  # 使用 doctor-patient-communication 专业版
```

### 示例 3：合规检查

**触发词：** "检查合规"、"合规审查"、"对外发布"

```python
# 自动检查对外内容
from skills.aimed.compliance_check import check_public_content

result = check_public_content(website_text)
if not result["compliant"]:
    print(f"违规词汇：{result['violations']}")
    print(f"缺少声明：{result['missing']}")
```

## 技能开发规范

### 新增技能模板

```markdown
# Skill: [技能名称]

## 描述
[技能功能描述]

## 触发条件
- [触发场景 1]
- [触发场景 2]

## 工作流程
[详细步骤]

## 输出格式
[输出规范]

## 注意事项
[重要提醒]
```

### 命名规范
- 文件名：小写 + 连字符，如 `diagnostic-report-standard`
- 技能 ID：与文件名一致
- 避免使用空格、大写字母、下划线

### 文档要求
- 每个技能必须包含：描述、触发条件、工作流程
- 提供至少 1 个使用示例
- 更新 `skills/README.md` 技能清单

## 测试与验证

### 单元测试
```bash
# 运行技能库测试
python scripts/test_skills.py

# 测试单个技能
python -c "
from skills.aimed.diagnostic_report_standard import generate_report
report = generate_report(patient_id='test_001')
print(report)
"
```

### 集成测试
```bash
# 测试诊断 API 是否正确使用技能
curl -X POST http://localhost:18790/api/v1/diagnosis \
  -H "Content-Type: application/json" \
  -d '{"image": "test.jpg", "region": "stomach"}'
```

## 维护与更新

### 更新流程
1. 修改对应技能文件
2. 更新 `skills/README.md` 状态列
3. 运行测试脚本验证
4. 提交到 GitHub 仓库

### 版本管理
- 技能文件使用 Git 版本控制
- 重大变更更新文件头部版本号
- 保持向后兼容

## 常见问题

### Q: 技能不生效？
A: 检查配置文件中的 `external_dirs` 路径是否正确

### Q: 如何调试技能？
A: 查看 Hermes 日志：`journalctl -u hermes-gateway --follow`

### Q: 技能冲突怎么办？
A: 技能按加载顺序优先级，后加载的覆盖先加载的

## 联系与支持

- 技术问题：小超同学（钉钉）
- 使用问题：小菲同学（飞书）
- 文档更新：提交 PR 到 GitHub 仓库
