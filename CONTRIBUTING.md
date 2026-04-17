# 贡献指南 (Contributing Guide)

感谢你对 AIMED Agent Swarm 项目的关注！我们欢迎各种形式的贡献。

---

## 🤝 如何贡献

### 1. 报告问题 (Bug Report)

发现 Bug？请创建 Issue 并提供：

- **问题描述**：清晰描述问题现象
- **复现步骤**：如何触发这个问题
- **预期行为**：你认为应该发生什么
- **环境信息**：
  - Python 版本
  - 操作系统
  - 相关依赖版本

### 2. 功能建议 (Feature Request)

有新想法？请创建 Issue 并说明：

- **功能描述**：你想要什么功能
- **使用场景**：为什么需要这个功能
- **实现建议**：如果有想法可以分享

### 3. 提交代码 (Code Contribution)

#### 步骤：

1. **Fork 本仓库**
2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **开发并测试**
   ```bash
   # 安装开发依赖
   pip install -r requirements.txt
   
   # 运行测试
   pytest tests/ -v
   ```

4. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加新功能"
   ```

5. **推送到 Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **创建 Pull Request**

---

## 📝 代码规范

### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 变量/函数 | 小写 + 下划线 | `patient_id`, `diagnose_stomach()` |
| 类名 | 大驼峰 | `ConductorAgent`, `DiagnosisResult` |
| 常量 | 大写 + 下划线 | `MAX_IMAGE_SIZE`, `SUPPORTED_ORGANS` |
| 私有方法 | 单下划线前缀 | `_internal_method()` |

### 代码风格

- 遵循 **PEP 8** 风格指南
- 使用 **4 空格** 缩进
- 行宽限制 **100 字符**
- 函数添加 **文档字符串**

### 提交信息规范

格式：`<type>: <description>`

**Type 类型：**

| 类型 | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 文档更新 |
| `style` | 代码格式（不影响功能） |
| `refactor` | 重构 |
| `test` | 测试相关 |
| `chore` | 构建/工具/配置 |

**示例：**
```
feat: 添加胰腺诊断 API v1
fix: 修复报告生成时的空指针异常
docs: 更新 README 安装说明
refactor: 优化 Conductor Agent 任务调度逻辑
```

---

## 🧪 测试要求

### 单元测试

- 新功能必须包含单元测试
- 现有功能修改需确保测试通过
- 目标测试覆盖率：≥ 80%

```bash
# 运行所有测试
pytest tests/ -v

# 生成覆盖率报告
pytest --cov=agents --cov=routers --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### 测试用例命名

```python
def test_<function>_<scenario>_<expected_result>():
    # 示例
    def test_diagnose_stomach_valid_image_returns_result():
    def test_dispatch_task_invalid_organ_returns_error():
```

---

## 📚 文档要求

### 代码注释

- 公共函数/类必须添加 **docstring**
- 复杂逻辑需添加 **行内注释**
- 使用 **中文** 注释（本项目主要语言）

```python
def diagnose_stomach(image_path: str) -> DiagnosisResult:
    """
    胃超声影像诊断
    
    Args:
        image_path: 超声影像文件路径
        
    Returns:
        DiagnosisResult: 诊断结果
        
    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 图像格式不支持
    """
```

### 文档更新

以下情况需更新文档：

- ✅ 新增/修改 API 接口 → 更新 `API.md`
- ✅ 新增配置项 → 更新 `README.md` 和 `.env.example`
- ✅ 部署流程变化 → 更新 `DEPLOY.md`
- ✅ 重大功能变更 → 更新 `CHANGELOG.md`

---

## 🔀 Pull Request 流程

1. **PR 标题**：清晰描述变更内容
2. **PR 描述**：
   - 变更原因
   - 变更内容
   - 测试情况
   - 相关 Issue 链接
3. **代码审查**：等待维护者 Review
4. **CI 检查**：确保自动化测试通过
5. **合并**：审查通过后合并到主分支

### PR 模板

```markdown
## 变更类型
- [ ] 新功能 (feat)
- [ ] Bug 修复 (fix)
- [ ] 文档更新 (docs)
- [ ] 重构 (refactor)
- [ ] 其他 (chore)

## 变更描述
<!-- 详细描述你的变更 -->

## 测试情况
- [ ] 单元测试通过
- [ ] 手动测试完成
- [ ] 覆盖率报告（如适用）

## 相关 Issue
<!-- 链接到相关 Issue -->
```

---

## 📞 联系方式

- **GitHub Issues**: https://github.com/huang-carl/aimed-agi-ultrasound/issues
- **邮箱**: aimed@aius.xin
- **官网**: https://www.aius.xin

---

## 📄 开源协议

MIT License - 详见 [LICENSE](LICENSE)

---

**感谢你的贡献！** 🎉
