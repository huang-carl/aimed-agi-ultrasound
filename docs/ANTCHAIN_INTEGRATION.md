# AIMED 与蚂蚁链对接指南

**版本：** V1.0  
**创建时间：** 2026-04-27  
**状态：** Phase 2 规划

---

## 一、蚂蚁链简介

### 什么是蚂蚁链？
蚂蚁链（AntChain）是蚂蚁集团推出的区块链服务平台，提供：
- **身份存证**：医疗人员身份链上认证
- **数据存证**：诊断报告、影像数据不可篡改存证
- **智能合约**：自动化业务流程
- **隐私计算**：医疗数据可用不可见

### 为什么选择蚂蚁链？
| 优势 | 说明 |
|------|------|
| 国内合规 | 符合中国区块链信息服务备案要求 |
| 医疗场景 | 已有医疗数据存证成功案例 |
| 高性能 | 支持万级 TPS，满足医院并发需求 |
| 联盟链 | 适合医疗行业联盟场景 |
| 生态完善 | 阿里云生态集成，API 丰富 |

---

## 二、对接架构

```
┌─────────────────────────────────────────────────┐
│              AIMED 医疗系统                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ 医生工作台│  │ 患者咨询台│  │ 医院管理  │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │              │              │              │
│  ┌────┴──────────────┴──────────────┴─────┐       │
│  │        区块链服务层 (Hermes)            │       │
│  │  - 身份注册/验证                        │       │
│  │  - 数据存证/查询                        │       │
│  │  - 智能合约调用                         │       │
│  └──────────────────┬─────────────────────┘       │
└─────────────────────┼─────────────────────────────┘
                      │ HTTPS API
┌─────────────────────┼─────────────────────────────┐
│              蚂蚁链服务平台                        │
│  ┌──────────────────┴─────────────────────┐       │
│  │  BaaS 平台 (Blockchain as a Service)   │       │
│  │  - 身份管理                            │       │
│  │  - 数据存证                            │       │
│  │  - 智能合约                            │       │
│  └────────────────────────────────────────┘       │
└───────────────────────────────────────────────────┘
```

---

## 三、接入步骤

### 步骤 1：注册蚂蚁链账号
1. 访问 [蚂蚁链官网](https://www.antchain.com)
2. 注册企业账号（需要营业执照）
3. 实名认证（企业认证）
4. 创建应用（AIMED 医疗系统）

### 步骤 2：获取 API 凭证
| 凭证 | 说明 | 用途 |
|------|------|------|
| AppID | 应用唯一标识 | API 调用标识 |
| AppSecret | 应用密钥 | 签名验证 |
| AccessKey | 访问密钥 | API 认证 |
| SecretKey | 签名密钥 | 请求签名 |

### 步骤 3：选择服务类型
| 服务 | 适用场景 | 费用 |
|------|----------|------|
| **身份存证** | 医生/患者/医院身份认证 | 免费额度 + 按量计费 |
| **数据存证** | 诊断报告/影像数据存证 | 按存证次数计费 |
| **智能合约** | 自动化业务流程 | 按调用次数计费 |
| **隐私计算** | 医疗数据可用不可见 | 按计算量计费 |

### 步骤 4：开发集成
```python
# 示例：身份注册到蚂蚁链
import requests
import hashlib
import hmac
import time

class AntChainService:
    def __init__(self, app_id, app_secret, access_key, secret_key):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_key = access_key
        self.secret_key = secret_key
        self.base_url = "https://api.antchain.com"
    
    def register_identity(self, identity_data):
        """
        注册身份到蚂蚁链
        
        Args:
            identity_data: 身份数据字典
                - name: 姓名
                - id_type: 身份类型 (doctor/patient/hospital)
                - id_number: 身份证号/机构代码
                - certificate: 执业证书号
                - hash: 数据哈希 (SHA256)
        
        Returns:
            dict: 交易结果
                - tx_hash: 交易哈希
                - block_height: 区块高度
                - timestamp: 时间戳
        """
        # 1. 计算数据哈希
        data_hash = self._calculate_hash(identity_data)
        
        # 2. 构建请求
        request_data = {
            "app_id": self.app_id,
            "method": "antchain.identity.register",
            "timestamp": int(time.time() * 1000),
            "data": {
                "name": identity_data["name"],
                "id_type": identity_data["id_type"],
                "id_number": identity_data["id_number"],
                "certificate": identity_data.get("certificate", ""),
                "data_hash": data_hash
            }
        }
        
        # 3. 签名
        signature = self._sign(request_data)
        request_data["sign"] = signature
        
        # 4. 发送请求
        response = requests.post(
            f"{self.base_url}/api/v1/identity/register",
            json=request_data,
            headers={
                "Content-Type": "application/json",
                "X-Access-Key": self.access_key
            }
        )
        
        return response.json()
    
    def verify_identity(self, identity_hash):
        """
        验证身份真实性
        
        Args:
            identity_hash: 身份数据哈希
        
        Returns:
            dict: 验证结果
                - verified: 是否验证通过
                - tx_hash: 交易哈希
                - block_height: 区块高度
                - registered_at: 注册时间
        """
        response = requests.get(
            f"{self.base_url}/api/v1/identity/verify",
            params={"data_hash": identity_hash},
            headers={
                "X-Access-Key": self.access_key
            }
        )
        return response.json()
    
    def register_diagnosis(self, diagnosis_data):
        """
        注册诊断报告到蚂蚁链
        
        Args:
            diagnosis_data: 诊断数据字典
                - patient_id: 患者 ID
                - doctor_id: 医生 ID
                - diagnosis: 诊断结果
                - surads_class: Su-RADS 分类
                - report_hash: 报告哈希
        
        Returns:
            dict: 交易结果
        """
        # 计算报告哈希
        report_hash = self._calculate_hash(diagnosis_data)
        
        # 构建请求
        request_data = {
            "app_id": self.app_id,
            "method": "antchain.diagnosis.register",
            "timestamp": int(time.time() * 1000),
            "data": {
                "patient_id": diagnosis_data["patient_id"],
                "doctor_id": diagnosis_data["doctor_id"],
                "diagnosis": diagnosis_data["diagnosis"],
                "surads_class": diagnosis_data.get("surads_class", ""),
                "report_hash": report_hash
            }
        }
        
        # 签名并发送
        signature = self._sign(request_data)
        request_data["sign"] = signature
        
        response = requests.post(
            f"{self.base_url}/api/v1/diagnosis/register",
            json=request_data,
            headers={
                "Content-Type": "application/json",
                "X-Access-Key": self.access_key
            }
        )
        
        return response.json()
    
    def _calculate_hash(self, data):
        """计算数据 SHA256 哈希"""
        import json
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def _sign(self, data):
        """HMAC-SHA256 签名"""
        message = json.dumps(data, sort_keys=True)
        signature = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
```

---

## 四、AIMED 集成方案

### 4.1 Hermes 后端集成
```python
# services/blockchain_service.py
from antchain_service import AntChainService

class BlockchainService:
    def __init__(self):
        self.antchain = AntChainService(
            app_id="your_app_id",
            app_secret="your_app_secret",
            access_key="your_access_key",
            secret_key="your_secret_key"
        )
    
    async def register_doctor(self, doctor_data):
        """注册医生身份"""
        result = await self.antchain.register_identity({
            "name": doctor_data["name"],
            "id_type": "doctor",
            "id_number": doctor_data["license_number"],
            "certificate": doctor_data["certificate_number"],
            "hash": doctor_data["data_hash"]
        })
        return result
    
    async def register_diagnosis(self, diagnosis_data):
        """注册诊断报告"""
        result = await self.antchain.register_diagnosis({
            "patient_id": diagnosis_data["patient_id"],
            "doctor_id": diagnosis_data["doctor_id"],
            "diagnosis": diagnosis_data["diagnosis"],
            "surads_class": diagnosis_data["surads_class"],
            "report_hash": diagnosis_data["report_hash"]
        })
        return result
    
    async def verify_identity(self, identity_hash):
        """验证身份"""
        result = await self.antchain.verify_identity(identity_hash)
        return result
```

### 4.2 API 路由
```python
# routers/blockchain.py
from fastapi import APIRouter, Depends
from services.blockchain_service import BlockchainService

router = APIRouter()
blockchain = BlockchainService()

@router.post("/identity/register")
async def register_identity(identity_data: dict):
    """注册身份到蚂蚁链"""
    result = await blockchain.register_doctor(identity_data)
    return result

@router.get("/identity/verify")
async def verify_identity(identity_hash: str):
    """验证身份真实性"""
    result = await blockchain.verify_identity(identity_hash)
    return result

@router.post("/diagnosis/register")
async def register_diagnosis(diagnosis_data: dict):
    """注册诊断报告到蚂蚁链"""
    result = await blockchain.register_diagnosis(diagnosis_data)
    return result
```

### 4.3 前端集成
```javascript
// portal/blockchain-identity.html
async function registerIdentity() {
    const identityData = {
        name: document.getElementById('name').value,
        id_type: document.getElementById('idType').value,
        id_number: document.getElementById('idNumber').value,
        certificate: document.getElementById('certificate').value
    };
    
    try {
        const response = await fetch('/api/v1/identity/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(identityData)
        });
        
        const result = await response.json();
        
        if (result.tx_hash) {
            alert(`身份注册成功！\n交易哈希：${result.tx_hash}\n区块高度：${result.block_height}`);
        }
    } catch (error) {
        alert('注册失败：' + error.message);
    }
}
```

---

## 五、数据存证方案

### 5.1 身份存证
| 数据 | 存证内容 | 哈希算法 |
|------|----------|----------|
| 医生身份 | 姓名 + 执业证号 + 机构 | SHA256 |
| 患者身份 | 姓名 + 身份证号（脱敏） | SHA256 |
| 医院资质 | 机构代码 + 执业许可证 | SHA256 |

### 5.2 诊断报告存证
| 数据 | 存证内容 | 存储方式 |
|------|----------|----------|
| 诊断结果 | Su-RADS 分类 + 医生意见 | 链上存证 |
| 影像数据 | 影像哈希 + 存储地址 | IPFS + 链上 |
| 报告文件 | 报告哈希 + 签名 | 链上存证 |

### 5.3 隐私保护
- 患者身份信息脱敏处理
- 医疗数据哈希上链（原文不上传）
- 零知识证明验证（Phase 3）

---

## 六、费用估算

| 服务 | 免费额度 | 超出费用 | 预估月费用 |
|------|----------|----------|------------|
| 身份存证 | 1000 次/月 | 0.01 元/次 | 50-200 元 |
| 数据存证 | 500 次/月 | 0.02 元/次 | 100-500 元 |
| 智能合约 | 100 次/月 | 0.05 元/次 | 50-300 元 |
| 隐私计算 | 试用 | 按量计费 | 待评估 |

**总预估：** 200-1000 元/月（根据实际使用量）

---

## 七、实施计划

### Phase 2.1（2026 Q3）
- [ ] 注册蚂蚁链企业账号
- [ ] 获取 API 凭证
- [ ] 开发身份存证功能
- [ ] 测试环境验证

### Phase 2.2（2026 Q4）
- [ ] 诊断报告存证功能
- [ ] IPFS 集成
- [ ] 生产环境部署
- [ ] 合规审查

### Phase 3（2027 Q1+）
- [ ] 智能合约开发
- [ ] 隐私计算集成
- [ ] 跨链互操作
- [ ] 零知识证明

---

## 八、合规要求

### 医疗数据合规
- ✅ 符合《个人信息保护法》
- ✅ 符合《数据安全法》
- ✅ 符合《网络安全法》
- ✅ 符合《区块链信息服务管理规定》

### 区块链备案
- 需要向国家网信办备案
- 提供区块链信息服务名称、功能、适用范围
- 定期提交安全评估报告

---

## 九、联系方式

### 蚂蚁链官方
- 官网：https://www.antchain.com
- 技术支持：support@antchain.com
- 商务咨询：business@antchain.com

### AIMED 项目
- 技术负责人：小超同学
- 项目负责人：Skytop 总
- 联系方式：通过钉钉联系

---

_对接指南 V1.0，持续更新中..._
