# 区块链对接文档

## 概述

AIMED 充盈视界已集成区块链服务，支持多链适配器架构。当前默认使用**腾讯至信链**，同时预留了蚂蚁链和 FISCO BCOS 的适配接口。

## 架构

```
┌─────────────────────────────────────────────────────────┐
│                    AIMED 前端 (Portal)                   │
│  区块链身份注册 → 调用后端 API → 获取 DID/存证           │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              Hermes 后端 (18790 端口)                    │
│                                                     │
│  ┌─────────────┐  ┌─────────────┐                   │
│  │ DID 管理模块 │  │ 存证管理模块 │                   │
│  │             │  │             │                   │
│  │ - 注册身份  │  │ - 报告存证  │                   │
│  │ - 验证身份  │  │ - 数据溯源  │                   │
│  │ - 身份查询  │  │ - 哈希验证  │                   │
│  └──────┬──────┘  └──────┬──────┘                   │
│         │                │                           │
└─────────┼────────────────┼───────────────────────────┘
          │                │
          ▼                ▼
┌───────────────────────────────────────────────────────┐
│              区块链适配器层                            │
│                                                     │
│  - TencentZhixinAdapter (腾讯至信链) ✅ 已启用       │
│  - AntChainAdapter (蚂蚁链) ⏳ 待配置               │
│  - FiscoBcosAdapter (FISCO BCOS) ⏳ 待配置          │
└───────────────────────────────────────────────────────┘
```

## API 接口

### DID 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/blockchain/did/register` | 注册链上数字身份 |
| POST | `/api/v1/blockchain/did/verify` | 验证链上身份 |
| GET | `/api/v1/blockchain/did/{did}` | 查询身份详情 |

### 存证接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/blockchain/evidence/store` | 数据上链存证 |
| POST | `/api/v1/blockchain/evidence/verify` | 验证存证 |
| GET | `/api/v1/blockchain/evidence/{evidence_id}` | 查询存证详情 |

### 状态接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/blockchain/status` | 获取链状态 |
| GET | `/api/v1/blockchain/chains` | 获取所有可用链 |

## 配置

配置文件：`/root/.openclaw/workspace/config/blockchain.json`

```json
{
  "provider": "tencent_zhixin",
  "app_key": "zx1f552e4b0849269f9889b225dc8dab70dd187d31",
  "app_secret": "待补充",
  "status": "ready",
  "services": {
    "did": true,
    "evidence": true,
    "contract": false
  }
}
```

## 使用示例

### 1. 注册数字身份

```bash
curl -X POST http://localhost:18790/api/v1/blockchain/did/register \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "doctor_001",
    "user_type": "doctor",
    "metadata": {
      "name": "张医生",
      "hospital": "南京大学附属医院"
    }
  }'
```

响应：
```json
{
  "success": true,
  "data": {
    "status": "success",
    "did": "did:zhixin:doctor_001:abc12345",
    "tx_hash": "9ed0e1fa0ee540a98c694dcd595dca17",
    "user_id": "doctor_001",
    "user_type": "doctor",
    "chain": "tencent_zhixin"
  }
}
```

### 2. 诊断报告存证

```bash
curl -X POST http://localhost:18790/api/v1/blockchain/evidence/store \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "patient_id": "P001",
      "diagnosis": "Su-RADS 3",
      "doctor_id": "doctor_001"
    },
    "metadata": {
      "type": "diagnosis_report"
    }
  }'
```

### 3. 验证身份

```bash
curl -X POST http://localhost:18790/api/v1/blockchain/did/verify \
  -H "Content-Type: application/json" \
  -d '{"did": "did:zhixin:doctor_001:abc12345"}'
```

## 前端集成

### 区块链身份页面

访问 `/portal/blockchain-identity.html` 可注册区块链身份：
- 选择身份类型（患者/医生/开发者/管理员）
- 填写个人信息
- 点击「注册到区块链」调用后端 API
- 获取 DID 和交易哈希

### 登录页面

访问 `/portal/login.html` 可使用区块链身份登录：
- 选择「区块链身份」标签
- 输入 DID
- 选择登录身份
- 点击「区块链身份验证登录」

## 下一步

1. **补充 AppSecret**：获取至信链的 AppSecret 并更新配置
2. **开通 API 权限**：在至信链控制台开通 DID 和存证服务
3. **测试真实 API**：使用真实 API 调用替代模拟数据
4. **多链支持**：根据需要启用蚂蚁链或 FISCO BCOS
5. **智能合约**：部署自定义合约实现复杂业务逻辑

## 注意事项

⚠️ **当前状态**：API 调用使用模拟数据（mock 模式）
- DID 注册/验证返回模拟结果
- 存证服务返回模拟结果
- 前端页面正常显示，体验流程完整

✅ **真实 API 启用条件**：
- 补充 AppSecret
- 在至信链控制台开通服务
- 重启 Hermes 服务

## 文件清单

| 文件 | 说明 |
|------|------|
| `services/blockchain_service.py` | 区块链服务核心代码 |
| `routers/v1/blockchain.py` | API 路由 |
| `config/blockchain.json` | 区块链配置 |
| `static/portal/blockchain-identity.html` | 区块链身份页面 |
| `static/portal/login.html` | 登录页面（含区块链登录） |
