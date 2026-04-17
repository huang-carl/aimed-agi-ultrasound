# AIMED Agent Swarm

**充盈视界 FillingVision - 胃胰超声造影 AI 诊断系统**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)

---

## 🎯 项目简介

聚焦胃 + 胰腺 2 器官的充盈超声造影 AI 辅助诊断系统，为基层医疗机构提供高效、低成本、易部署的消化道疾病早筛解决方案。

---

## ⚡ 快速开始

```bash
# 克隆仓库
git clone https://github.com/huang-carl/aimed-agi-ultrasound.git
cd aimed-agi-ultrasound

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env

# 启动服务
python main.py

# 访问 API 文档
# http://localhost:8000/docs
```

---

## 📡 核心 API

| 接口 | 方法 | 功能 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/stomach/diagnose` | POST | 胃诊断 |
| `/api/pancreas/diagnose` | POST | 胰腺诊断 |
| `/api/conductor/dispatch` | POST | 任务分发 |
| `/api/report/generate` | POST | 报告生成 |

---

## 📚 文档

- [API 示例](docs/API_EXAMPLES.md)
- [部署检查清单](docs/DEPLOYMENT_CHECKLIST.md)
- [开发指南](docs/DEVELOPMENT_GUIDE.md)
- [贡献指南](CONTRIBUTING.md)
- [安全策略](SECURITY.md)

---

## 🤝 共建单位

- 阿尔麦德智慧医疗（湖州）有限公司
- 南京大学
- 湖州师范学院附属第一医院

---

## 📞 联系方式

- **官网：** https://www.aius.xin
- **邮箱：** aimed@aius.xin

---

## 📄 开源协议

MIT License
