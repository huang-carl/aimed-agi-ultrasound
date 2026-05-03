# 方案 A：统一域名部署方案

## 目标
整合 aius.xin（官网）和 aimed.aius.xin（AI 平台）到统一的架构中

## 架构设计

```
aius.xin (主域名)
├── /                    → 官网首页 (static/index.html)
├── /en                  → 英文官网
├── /portal/             → AI 平台入口
├── /api/                → Hermes API (18790 端口)
├── /docs                → API 文档
└── /redoc               → Redoc 文档

aimed.aius.xin (平台域名)
├── /                    → 平台首页 (重定向到 aius.xin/portal/)
├── /platform/           → 平台页面
├── /company/            → 公司知识库
└── /ecosystem/          → 生态文档
```

## 实施步骤

### 1. SSL 证书统一
- 使用 Let's Encrypt 通配符证书 *.aius.xin
- 覆盖 aius.xin 和 *.aius.xin 所有子域名

### 2. Nginx 配置整合
- 合并 aius.conf 和 aimed.conf
- 统一路由规则
- 优化缓存和安全头

### 3. 域名解析
- aius.xin → 8.141.91.165
- aimed.aius.xin → 8.141.91.165
- www.aius.xin → aius.xin

### 4. 服务配置
- Hermes 后端：18790 端口
- OpenClaw 前端：18789 端口
- Nginx 统一入口：80/443 端口

## 优势
- ✅ 统一域名管理
- ✅ 单一 SSL 证书
- ✅ 简化 DNS 配置
- ✅ 更好的 SEO
- ✅ 统一的安全策略

## 时间线
- 备份：✅ 已完成 (2026-05-03 10:39)
- 实施：✅ 已完成 (2026-05-03 10:45)
- 验证：✅ 已完成

## 实施结果

### Nginx 配置
- ✅ 创建统一配置 `/etc/nginx/conf.d/aius-unified.conf`
- ✅ 备份旧配置 `aius.conf.bak` + `aimed.conf.bak`
- ✅ 配置测试通过
- ✅ Nginx 重启成功

### 服务验证
| 端点 | 状态 | 说明 |
|------|------|------|
| https://aius.xin/ | ✅ 200 | 官网首页正常 |
| https://aimed.aius.xin/ | ✅ 200 | AI 平台正常 |
| https://aius.xin/health | ✅ 200 | Hermes API 正常 |
| https://aius.xin/portal/ | ✅ 200 | 平台入口正常 |
| https://aius.xin/api/ | ✅ 代理 | Hermes 后端代理 |

### 域名架构
```
aius.xin (主域名)
├── /                    → 官网首页 ✅
├── /en                  → 英文官网 ✅
├── /longnao             → 龙脑产品 ✅
├── /demo                → 演示页面 ✅
├── /portal/             → AI 平台入口 ✅
├── /platform/           → 平台页面 ✅
├── /company/            → 公司知识库 ✅
├── /ecosystem/          → 生态文档 ✅
├── /uploads/            → 上传文件 ✅
├── /api/                → Hermes API ✅
├── /docs                → API 文档 ✅
└── /redoc               → Redoc 文档 ✅

aimed.aius.xin (平台域名)
├── /                    → 平台首页 ✅
├── /platform/           → 平台页面 ✅
├── /company/            → 公司知识库 ✅
└── /ecosystem/          → 生态文档 ✅

longnao.aius.xin (产品域名)
└── /                    → 龙脑产品 ✅
```

### SSL 证书
- aius.xin: Let's Encrypt ✅
- aimed.aius.xin: 独立证书 ✅
- longnao.aius.xin: Let's Encrypt ✅

### 安全配置
- ✅ HSTS (max-age=31536000; includeSubDomains)
- ✅ X-Frame-Options: SAMEORIGIN
- ✅ X-Content-Type-Options: nosniff
- ✅ X-XSS-Protection: 1; mode=block
- ✅ Referrer-Policy: strict-origin-when-cross-origin

## 知识库修复
- ✅ 创建 `/ecosystem/index.html`（生态合作入口页）
- ✅ 创建 `/ecosystem/生态合作/index.html`（生态合作详情）
- ✅ 修复 403 错误

## 下一步
- [ ] 配置通配符证书 *.aius.xin（简化证书管理）
- [ ] 添加 DNS 监控
- [ ] 设置证书自动续期
- [ ] 性能优化（Gzip/Brotli 压缩）
