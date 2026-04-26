# AIMED 官网 V1.0 基线模板

**版本：** V1.0  
**日期：** 2026-04-26  
**状态：** ✅ 基线版本（后续迭代基础）

---

## 📁 文件清单

### 官网首页
- `index.html` - 官网首页（国际大厂风格）
- `aimed-logo-new.jpg` - 品牌 Logo

### 产品页面
- `products.html` - 产品中心
- `solutions.html` - 解决方案
- `technology.html` - 技术架构
- `upload.html` - 数据上传
- `demo.html` - 演示系统
- `longnao.html` - 龙脑产品（独立项目）

### AI 平台（Portal）
- `portal/index.html` - 平台入口页
- `portal/login.html` - 统一登录页
- `portal/doctor.html` - 医生工作台
- `portal/patient.html` - 患者咨询台
- `portal/blockchain-identity.html` - 区块链身份识别
- `portal/digital-assets.html` - 数字资产管理
- `portal/developer.html` - 开发者中心

---

## 🎨 设计特点

| 特点 | 说明 |
|------|------|
| **设计风格** | 国际大厂风格（Apple/Google/Microsoft） |
| **色彩系统** | CSS Variables 全局统一 |
| **响应式** | 桌面版 + 手机版适配 |
| **导航栏** | 毛玻璃效果（backdrop-filter blur） |
| **卡片设计** | 圆角 + 悬停动画 |
| **字体** | SF Pro Display + PingFang SC |

---

## 📊 内容结构

### 官网首页（index.html）
1. Hero 区域 - 价值主张
2. 统计数字 - 核心数据
3. 关于阿尔麦德 - 公司简介
4. 四大技术支柱 - 核心技术
5. 四大运用场景 - 应用场景
6. 合作伙伴 - 产学研医
7. 三阶段路线图 - 实施规划
8. AI 诊断演示 - 快速体验
9. 联合实验室 - 平台入口
10. 联系我们 - 联系方式

### AI 平台（Portal）
1. 统一登录 - 账号密码/区块链身份
2. 医生工作台 - AI 诊断/报告导出
3. 患者咨询台 - 症状咨询/AI 建议
4. 区块链身份 - 身份注册/链上存证
5. 数字资产 - 报告管理/NFT 存证

---

## 🔧 技术实现

| 技术 | 说明 |
|------|------|
| **前端** | 纯 HTML/CSS/JS（无框架依赖） |
| **后端** | FastAPI (Hermes V2.1) |
| **数据库** | SQLite (cases.db) |
| **向量库** | ChromaDB (23 条文档) |
| **AI 模型** | 4 个（qwen3.5-plus/nvidia/zhipu/deepseek） |
| **SSL** | Let's Encrypt (aius.xin) |
| **部署** | Nginx + systemd |

---

## 📝 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| V1.0 | 2026-04-26 | 基线版本（国际大厂风格） |

---

## 📋 后续迭代计划

| 阶段 | 内容 | 优先级 |
|------|------|--------|
| V1.1 | 汉堡菜单 + 响应式优化 | 🔴 高 |
| V1.2 | API 文档 + 速率限制 | 🟡 中 |
| V2.0 | 真实联盟链接入 | 🟡 中 |

---

**备份位置：** `static/templates/v1.0/`  
**基线版本：** V1.0 (2026-04-26)
