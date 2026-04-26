# 开发指南 (Development Guide)

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/huang-carl/aimed-agi-ultrasound.git
cd aimed-agi-ultrasound
```

### 2. 创建虚拟环境

```bash
# Python 3.10+
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows
```

### 3. 安装依赖

```bash
# 生产依赖
pip install -r requirements.txt

# 开发依赖（推荐）
pip install pytest-cov black flake8 bandit pre-commit
```

### 4. 配置环境

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，至少配置
：
# - DASHSCOPE_API_KEY（阿里云百炼 API Key）
# - JWT_SECRET_KEY（生产环境必须修改）
```

### 5. 启动开发服务器

```bash
# 方式一：使用 Makefile
make run

# 方式二：直接启动
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档。

---

## 🏗️ 项目结构

```
aimed-agi-ultrasound/
├── main.py                      # FastAPI 应用入口
├── config.py                    # 配置管理
├── requirements.txt             # Python 依赖
├── .env                         # 环境变量（不提交）
├── .env.example                 # 环境变量模板
│
├── agents/                      # AI 智能体模块
│   ├── __init__.py
│   ├── conductor_agent.py       # 总指挥 Agent
│   ├── stomach_agent.py         # 胃诊断 Agent
│   ├── pancreas_agent.py        # 胰腺诊断 Agent
│   └── report_agent.py          # 报告生成 Agent
│
├── routers/                     # API 路由模块
│   ├── __init__.py
│   ├── conductor.py             # 总指挥路由
│   ├── stomach.py               # 胃诊断路由
│   ├── pancreas.py              # 胰腺诊断路由
│   ├── report.py                # 报告生成路由
│   └── v1/                      # API v1 版本
│       ├── __init__.py
│       ├── conductor.py
│       ├── stomach.py
│       ├── pancreas.py
│       └── report.py
│
├── middleware/                  # 中间件模块
│   ├── __init__.py
│   └── exceptions.py            # 全局异常处理
│
├── tests/                       # 测试用例
│   ├── __init__.py
│   ├── test_conductor.py
│   ├── test_stomach.py
│   ├── test_pancreas.py
│   └── test_report.py
│
├── deploy/                      # 部署配置
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── docs/                        # 文档目录
│   ├── API_EXAMPLES.md
│   ├── DEPLOYMENT_CHECKLIST.md
│   └── DEVELOPMENT_GUIDE.md
│
├── data/                        # 数据目录
│   ├── samples/                 # 测试样本
│   └── reports/                 # 生成的报告
│
└── models/                      # 模型权重目录
```

---

## 📝 开发规范

### 代码风格

- 遵循 **PEP 8** 风格指南
- 使用 **Black** 格式化代码
- 使用 **isort** 排序 import
- 行宽限制 **100 字符**

```bash
# 格式化代码
black agents/ routers/ main.py config.py --line-length 100

# 排序 import
isort agents/ routers/ main.py config.py --profile black --line-length 100
```

### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 变量/函数 | 小写 + 下划线 | `patient_id`, `diagnose()` |
| 类名 | 大驼峰 | `ConductorAgent` |
| 常量 | 大写 + 下划线 | `SUPPORTED_ORGANS` |
| 私有方法 | 单下划线前缀 | `_internal_process()` |

### 文档字符串

所有公共函数和类必须添加 docstring：

```python
def diagnose_stomach(image_path: str) -> DiagnosisResult:
    """
    胃超声影像诊断
    
    Args:
        image_path: 超声影像文件路径
        
    Returns:
        DiagnosisResult: 诊断结果，包含疾病名称、置信度、建议
        
    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 图像格式不支持
        
    Example:
        >>> result = diagnose_stomach("stomach.png")
        >>> print(result.disease)
        慢性胃炎
    """
```

---

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_stomach.py -v

# 生成覆盖率报告
pytest --cov=agents --cov=routers --cov=main --cov=config --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### 编写测试

测试文件命名：`test_<module>.py`

测试函数命名：`test_<function>_<scenario>_<expected>`

```python
def test_diagnose_stomach_valid_image_returns_result():
    """测试有效图像返回诊断结果"""
    # Arrange
    agent = StomachAgent()
    
    # Act
    result = agent.diagnose("test_image.png")
    
    # Assert
    assert result is not None
    assert result.organ == "胃"
    assert 0 <= result.probability <= 1
```

---

## 🔧 常用命令

### Makefile 命令

```bash
make help           # 显示帮助信息
make install        # 安装生产依赖
make dev            # 安装开发依赖
make run            # 启动开发服务器
make test           # 运行测试
make coverage       # 生成覆盖率报告
make lint           # 代码检查
make format         # 格式化代码
make clean          # 清理临时文件
```

### Git 命令

```bash
# 提交前检查
pre-commit run --all-files

# 查看变更
git diff

# 提交代码
git add .
git commit -m "feat: 添加新功能"
```

---

## 🐛 调试技巧

### 启用调试模式

编辑 `.env` 文件：

```env
DEBUG=true
LOG_LEVEL=DEBUG
```

### 使用断点

```python
import pdb; pdb.set_trace()  # 传统断点
# 或
breakpoint()  # Python 3.7+
```

### 查看日志

```bash
# 实时查看日志
tail -f logs/aimed.log

# 查看错误日志
grep ERROR logs/aimed.log | tail -20
```

---

## 📦 添加新功能

### 步骤

1. **创建分支**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **实现功能**
   - 在 `agents/` 添加 Agent 逻辑
   - 在 `routers/` 添加 API 路由
   - 编写测试用例

3. **运行测试**
   ```bash
   pytest tests/ -v
   ```

4. **提交代码**
   ```bash
   git add .
   git commit -m "feat: 添加新功能"
   ```

5. **创建 PR**
   - 推送到 GitHub
   - 创建 Pull Request
   - 等待代码审查

---

## 🚀 部署

参考 [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

---

## 📞 获取帮助

- **GitHub Issues:** https://github.com/huang-carl/aimed-agi-ultrasound/issues
- **邮箱：** aimed@aius.xin
- **文档：** https://github.com/huang-carl/aimed-agi-ultrasound/tree/main/docs

---

**最后更新：** 2026-04-18
