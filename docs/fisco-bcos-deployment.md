# FISCO BCOS 部署指南

## 概述

FISCO BCOS 是完全开源免费的联盟链平台，适合 AIMED 医疗数据存证场景。

## 系统要求

| 资源 | 最低要求 | 推荐配置 |
|------|----------|----------|
| CPU | 2 核 | 4 核+ |
| 内存 | 2GB | 4GB+ |
| 磁盘 | 20GB | 50GB+ |
| 网络 | 10Mbps | 100Mbps+ |

## 部署方式

### 方式一：单机测试网（推荐 Phase 1）

```bash
# 1. 安装依赖
sudo yum install -y python3 curl wget

# 2. 下载部署脚本
cd /tmp
curl -LO https://github.com/FISCO-BCOS/FISCO-BCOS/releases/download/v3.16.3/build_chain.sh
chmod +x build_chain.sh

# 3. 部署 4 节点测试网
./build_chain.sh -l 127.0.0.1:4 -p 30300,20200,8545

# 4. 启动节点
bash nodes/127.0.0.1/start_all.sh

# 5. 验证状态
bash nodes/127.0.0.1/check_status.sh
```

### 方式二：多机联盟链（推荐 Phase 2）

```bash
# 每个机构部署一个节点
./build_chain.sh -l node1:1,node2:1,node3:1,node4:1 -p 30300,20200,8545
```

## 智能合约部署

### 1. 编写 DID 合约

```solidity
// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.6.10;

contract DIDRegistry {
    struct DIDDocument {
        string did;
        string userType;
        string metadata;
        uint256 createdAt;
        bool active;
    }
    
    mapping(string => DIDDocument) public dids;
    string[] public didList;
    
    event DIDRegistered(string did, string userType, uint256 timestamp);
    
    function registerDID(
        string memory did,
        string memory userType,
        string memory metadata
    ) public {
        require(!dids[did].active, "DID already exists");
        
        dids[did] = DIDDocument({
            did: did,
            userType: userType,
            metadata: metadata,
            createdAt: block.timestamp,
            active: true
        });
        
        didList.push(did);
        emit DIDRegistered(did, userType, block.timestamp);
    }
    
    function verifyDID(string memory did) public view returns (bool) {
        return dids[did].active;
    }
    
    function queryDID(string memory did) public view returns (
        string memory,
        string memory,
        string memory,
        uint256,
        bool
    ) {
        DIDDocument storage doc = dids[did];
        return (doc.did, doc.userType, doc.metadata, doc.createdAt, doc.active);
    }
}
```

### 2. 编写存证合约

```solidity
// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.6.10;

contract EvidenceStore {
    struct Evidence {
        string evidenceId;
        string dataHash;
        string metadata;
        uint256 blockNumber;
        uint256 timestamp;
    }
    
    mapping(string => Evidence) public evidences;
    string[] public evidenceList;
    
    event EvidenceStored(string evidenceId, string dataHash, uint256 timestamp);
    
    function storeEvidence(
        string memory evidenceId,
        string memory dataHash,
        string memory metadata
    ) public {
        require(bytes(evidences[evidenceId].evidenceId).length == 0, "Evidence exists");
        
        evidences[evidenceId] = Evidence({
            evidenceId: evidenceId,
            dataHash: dataHash,
            metadata: metadata,
            blockNumber: block.number,
            timestamp: block.timestamp
        });
        
        evidenceList.push(evidenceId);
        emit EvidenceStored(evidenceId, dataHash, block.timestamp);
    }
    
    function verifyEvidence(string memory evidenceId) public view returns (bool) {
        return bytes(evidences[evidenceId].evidenceId).length > 0;
    }
    
    function queryEvidence(string memory evidenceId) public view returns (
        string memory,
        string memory,
        string memory,
        uint256,
        uint256
    ) {
        Evidence storage ev = evidences[evidenceId];
        return (ev.evidenceId, ev.dataHash, ev.metadata, ev.blockNumber, ev.timestamp);
    }
}
```

## Python SDK 集成

### 1. 安装 SDK

```bash
pip3 install fisco-bcos-python-sdk
```

### 2. 配置 Hermes 后端

更新 `config/blockchain.json`：

```json
{
  "provider": "fisco_bcos",
  "fisco_bcos": {
    "node_url": "http://localhost:8545",
    "group_id": 1,
    "contract_address": "0x...",
    "private_key": "..."
  }
}
```

### 3. 测试连接

```python
from fisco_bcos_sdk import Client

client = Client(
    node_url="http://localhost:8545",
    group_id=1
)

# 测试连接
status = client.get_status()
print(f"链状态：{status}")
```

## 验证部署

### 1. 检查节点状态

```bash
# 查看节点日志
tail -f nodes/127.0.0.1/node0/log/log.INFO

# 查看区块高度
curl -X POST http://localhost:8545 -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"getBlockNumber","params":[],"id":1}'
```

### 2. 测试 API

```bash
# 注册 DID
curl -X POST http://localhost:18790/api/v1/blockchain/did/register \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_001", "user_type": "doctor"}'

# 存证
curl -X POST http://localhost:18790/api/v1/blockchain/evidence/store \
  -H "Content-Type: application/json" \
  -d '{"data": "test data", "metadata": {"type": "test"}}'
```

## 监控与维护

### 日志查看

```bash
# 实时查看日志
tail -f nodes/127.0.0.1/node0/log/log.INFO

# 查看错误日志
grep ERROR nodes/127.0.0.1/node0/log/log.INFO
```

### 性能监控

```bash
# 查看节点资源使用
top -p $(pgrep -f fisco-bcos)

# 查看磁盘使用
df -h nodes/
```

## 常见问题

### 1. 节点启动失败

```bash
# 检查端口占用
netstat -tlnp | grep -E "30300|20200|8545"

# 检查日志
tail -50 nodes/127.0.0.1/node0/log/log.INFO
```

### 2. 合约部署失败

```bash
# 检查 SDK 版本
pip3 show fisco-bcos-python-sdk

# 检查节点连接
curl -X POST http://localhost:8545 -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"getGroupList","params":[],"id":1}'
```

## 下一步

1. 部署测试网节点
2. 编译并部署智能合约
3. 更新 Hermes 配置
4. 测试 DID 注册和存证
5. 前端页面集成
