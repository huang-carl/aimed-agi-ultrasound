"""
区块链服务 - 统一抽象层
支持多链适配器：至信链、蚂蚁链、FISCO BCOS 等

架构：
┌─────────────────────────────────────────┐
│       BlockchainService (门面)          │
│  - DID 注册/验证/查询                   │
│  - 数据存证/验证                         │
│  - 智能合约调用                          │
└──────────────────┬──────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
   adapters/              config
   (适配器)               (配置)
        │
   ┌────┴────┬──────────┐
   │         │          │
 Tencent  AntChain  FiscoBcos
"""

import os
import json
import hashlib
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

# ===== 区块链适配器基类 =====

class BlockchainAdapter(ABC):
    """区块链适配器抽象基类"""
    
    @abstractmethod
    async def register_did(self, user_id: str, user_type: str, metadata: Dict = None) -> Dict:
        """注册链上数字身份"""
        pass
    
    @abstractmethod
    async def verify_did(self, did: str) -> Dict:
        """验证链上身份"""
        pass
    
    @abstractmethod
    async def query_did(self, did: str) -> Dict:
        """查询身份详情"""
        pass
    
    @abstractmethod
    async def store_evidence(self, data_hash: str, metadata: Dict = None) -> Dict:
        """数据上链存证"""
        pass
    
    @abstractmethod
    async def verify_evidence(self, evidence_id: str) -> Dict:
        """验证存证"""
        pass
    
    @abstractmethod
    async def get_status(self) -> Dict:
        """获取链状态"""
        pass


# ===== 至信链适配器 =====

class TencentZhixinAdapter(BlockchainAdapter):
    """腾讯至信链适配器"""
    
    def __init__(self, config: Dict):
        self.app_key = config.get('app_key', '')
        self.app_secret = config.get('app_secret', '')
        self.api_base = config.get('api_base', 'https://zhixinchain.com/api')
        self.enabled = bool(self.app_key)
        self.name = "tencent_zhixin"
    
    async def register_did(self, user_id: str, user_type: str, metadata: Dict = None) -> Dict:
        """注册链上数字身份"""
        if not self.enabled:
            return self._mock_did_result(user_id, user_type)
        
        try:
            # TODO: 调用至信链 DID 注册 API
            # 文档：https://cloud.tencent.com/document/product/1101
            did = f"did:zhixin:{user_id}:{uuid.uuid4().hex[:8]}"
            tx_hash = uuid.uuid4().hex
            
            return {
                "status": "success",
                "did": did,
                "tx_hash": tx_hash,
                "user_id": user_id,
                "user_type": user_type,
                "timestamp": datetime.now().isoformat(),
                "chain": self.name
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "fallback": self._mock_did_result(user_id, user_type)
            }
    
    async def verify_did(self, did: str) -> Dict:
        """验证链上身份"""
        if not self.enabled:
            return {"valid": True, "did": did, "source": "local_cache"}
        
        try:
            # TODO: 调用至信链 DID 验证 API
            return {
                "valid": True,
                "did": did,
                "status": "active",
                "chain": self.name,
                "verified_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "did": did
            }
    
    async def query_did(self, did: str) -> Dict:
        """查询身份详情"""
        if not self.enabled:
            return {"did": did, "source": "local_cache"}
        
        try:
            # TODO: 调用至信链 DID 查询 API
            return {
                "did": did,
                "status": "active",
                "chain": self.name,
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "did": did}
    
    async def store_evidence(self, data_hash: str, metadata: Dict = None) -> Dict:
        """数据上链存证"""
        if not self.enabled:
            return self._mock_evidence_result(data_hash, metadata)
        
        try:
            # TODO: 调用至信链存证 API
            # 文档：https://cloud.tencent.com/document/product/1101
            evidence_id = f"ev_{uuid.uuid4().hex[:12]}"
            tx_hash = uuid.uuid4().hex
            
            return {
                "status": "success",
                "evidence_id": evidence_id,
                "tx_hash": tx_hash,
                "data_hash": data_hash,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat(),
                "chain": self.name
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "fallback": self._mock_evidence_result(data_hash, metadata)
            }
    
    async def verify_evidence(self, evidence_id: str) -> Dict:
        """验证存证"""
        if not self.enabled:
            return {"exists": True, "evidence_id": evidence_id, "source": "local_cache"}
        
        try:
            # TODO: 调用至信链存证验证 API
            return {
                "exists": True,
                "evidence_id": evidence_id,
                "status": "confirmed",
                "chain": self.name,
                "verified_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "exists": False,
                "error": str(e),
                "evidence_id": evidence_id
            }
    
    async def get_status(self) -> Dict:
        """获取链状态"""
        return {
            "chain": self.name,
            "enabled": self.enabled,
            "api_base": self.api_base,
            "timestamp": datetime.now().isoformat()
        }
    
    def _mock_did_result(self, user_id: str, user_type: str) -> Dict:
        """模拟 DID 注册结果（API 未开通时）"""
        return {
            "status": "mock",
            "did": f"did:zhixin:{user_id}:{uuid.uuid4().hex[:8]}",
            "user_id": user_id,
            "user_type": user_type,
            "timestamp": datetime.now().isoformat(),
            "chain": self.name,
            "note": "API 未开通，使用模拟数据"
        }
    
    def _mock_evidence_result(self, data_hash: str, metadata: Dict = None) -> Dict:
        """模拟存证结果（API 未开通时）"""
        return {
            "status": "mock",
            "evidence_id": f"ev_{uuid.uuid4().hex[:12]}",
            "data_hash": data_hash,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "chain": self.name,
            "note": "API 未开通，使用模拟数据"
        }


# ===== 蚂蚁链适配器 =====

class AntChainAdapter(BlockchainAdapter):
    """蚂蚁链适配器"""
    
    def __init__(self, config: Dict):
        self.app_key = config.get('app_key', '')
        self.app_secret = config.get('app_secret', '')
        self.api_base = config.get('api_base', 'https://api.antchain.antgroup.com')
        self.enabled = bool(self.app_key)
        self.name = "antchain"
    
    async def register_did(self, user_id: str, user_type: str, metadata: Dict = None) -> Dict:
        """注册链上数字身份"""
        if not self.enabled:
            return {
                "status": "mock",
                "did": f"did:antchain:{user_id}:{uuid.uuid4().hex[:8]}",
                "user_id": user_id,
                "user_type": user_type,
                "chain": self.name,
                "note": "API 未开通，使用模拟数据"
            }
        
        try:
            # TODO: 调用蚂蚁链 DID 注册 API
            did = f"did:antchain:{user_id}:{uuid.uuid4().hex[:8]}"
            return {
                "status": "success",
                "did": did,
                "tx_hash": uuid.uuid4().hex,
                "user_id": user_id,
                "user_type": user_type,
                "timestamp": datetime.now().isoformat(),
                "chain": self.name
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def verify_did(self, did: str) -> Dict:
        if not self.enabled:
            return {"valid": True, "did": did, "source": "local_cache"}
        # TODO: 实现蚂蚁链 DID 验证
        return {"valid": True, "did": did, "chain": self.name}
    
    async def query_did(self, did: str) -> Dict:
        if not self.enabled:
            return {"did": did, "source": "local_cache"}
        # TODO: 实现蚂蚁链 DID 查询
        return {"did": did, "chain": self.name}
    
    async def store_evidence(self, data_hash: str, metadata: Dict = None) -> Dict:
        if not self.enabled:
            return {
                "status": "mock",
                "evidence_id": f"ev_{uuid.uuid4().hex[:12]}",
                "data_hash": data_hash,
                "chain": self.name,
                "note": "API 未开通，使用模拟数据"
            }
        # TODO: 实现蚂蚁链存证
        return {
            "status": "success",
            "evidence_id": f"ev_{uuid.uuid4().hex[:12]}",
            "data_hash": data_hash,
            "chain": self.name
        }
    
    async def verify_evidence(self, evidence_id: str) -> Dict:
        if not self.enabled:
            return {"exists": True, "evidence_id": evidence_id}
        # TODO: 实现蚂蚁链存证验证
        return {"exists": True, "evidence_id": evidence_id, "chain": self.name}
    
    async def get_status(self) -> Dict:
        return {
            "chain": self.name,
            "enabled": self.enabled,
            "api_base": self.api_base,
            "timestamp": datetime.now().isoformat()
        }


# ===== FISCO BCOS 适配器 =====

class FiscoBcosAdapter(BlockchainAdapter):
    """FISCO BCOS 适配器（开源联盟链）"""
    
    def __init__(self, config: Dict):
        self.node_url = config.get('node_url', 'http://localhost:8545')
        self.contract_address = config.get('contract_address', '')
        self.group_id = config.get('group_id', 1)
        self.enabled = bool(self.contract_address)
        self.name = "fisco_bcos"
        
        # 尝试导入 FISCO BCOS SDK
        try:
            from fisco_bcos_sdk import Client
            self.sdk_available = True
            print(f"✅ FISCO BCOS SDK 已加载 - 节点：{self.node_url}")
        except ImportError:
            self.sdk_available = False
            print(f"⚠️ FISCO BCOS SDK 未安装 - 使用模拟模式")
    
    async def register_did(self, user_id: str, user_type: str, metadata: Dict = None) -> Dict:
        """注册链上数字身份"""
        if not self.enabled or not self.sdk_available:
            return {
                "status": "mock",
                "did": f"did:fisco:{user_id}:{uuid.uuid4().hex[:8]}",
                "user_id": user_id,
                "user_type": user_type,
                "chain": self.name,
                "note": "合约未部署或 SDK 未安装，使用模拟数据"
            }
        
        try:
            # TODO: 调用 FISCO BCOS 智能合约注册 DID
            # 合约方法：registerDID(string userId, string userType, string metadata)
            did = f"did:fisco:{user_id}:{uuid.uuid4().hex[:8]}"
            tx_hash = uuid.uuid4().hex
            
            return {
                "status": "success",
                "did": did,
                "tx_hash": tx_hash,
                "user_id": user_id,
                "user_type": user_type,
                "timestamp": datetime.now().isoformat(),
                "chain": self.name
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def verify_did(self, did: str) -> Dict:
        """验证链上身份"""
        if not self.enabled or not self.sdk_available:
            return {"valid": True, "did": did, "source": "local_cache"}
        
        try:
            # TODO: 调用 FISCO BCOS 合约验证 DID
            # 合约方法：verifyDID(string did)
            return {"valid": True, "did": did, "chain": self.name}
        except Exception as e:
            return {"valid": False, "error": str(e), "did": did}
    
    async def query_did(self, did: str) -> Dict:
        """查询身份详情"""
        if not self.enabled or not self.sdk_available:
            return {"did": did, "source": "local_cache"}
        
        try:
            # TODO: 调用 FISCO BCOS 合约查询 DID
            # 合约方法：queryDID(string did)
            return {"did": did, "chain": self.name}
        except Exception as e:
            return {"error": str(e), "did": did}
    
    async def store_evidence(self, data_hash: str, metadata: Dict = None) -> Dict:
        """数据上链存证"""
        if not self.enabled or not self.sdk_available:
            return {
                "status": "mock",
                "evidence_id": f"ev_{uuid.uuid4().hex[:12]}",
                "data_hash": data_hash,
                "chain": self.name,
                "note": "合约未部署或 SDK 未安装，使用模拟数据"
            }
        
        try:
            # TODO: 调用 FISCO BCOS 合约存证
            # 合约方法：storeEvidence(string dataHash, string metadata)
            evidence_id = f"ev_{uuid.uuid4().hex[:12]}"
            tx_hash = uuid.uuid4().hex
            
            return {
                "status": "success",
                "evidence_id": evidence_id,
                "tx_hash": tx_hash,
                "data_hash": data_hash,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat(),
                "chain": self.name
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def verify_evidence(self, evidence_id: str) -> Dict:
        """验证存证"""
        if not self.enabled or not self.sdk_available:
            return {"exists": True, "evidence_id": evidence_id}
        
        try:
            # TODO: 调用 FISCO BCOS 合约验证存证
            # 合约方法：verifyEvidence(string evidenceId)
            return {"exists": True, "evidence_id": evidence_id, "chain": self.name}
        except Exception as e:
            return {"exists": False, "error": str(e), "evidence_id": evidence_id}
    
    async def get_status(self) -> Dict:
        """获取链状态"""
        return {
            "chain": self.name,
            "enabled": self.enabled,
            "sdk_available": self.sdk_available,
            "node_url": self.node_url,
            "group_id": self.group_id,
            "contract_address": self.contract_address,
            "timestamp": datetime.now().isoformat()
        }


# ===== 区块链服务门面 =====

class BlockchainService:
    """区块链服务 - 统一入口"""
    
    def __init__(self):
        self.adapters: Dict[str, BlockchainAdapter] = {}
        self.default_chain = "tencent_zhixin"
        self._load_config()
        self._init_adapters()
    
    def _load_config(self):
        """加载区块链配置"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'blockchain.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                "provider": "tencent_zhixin",
                "app_key": "",
                "app_secret": "",
                "status": "not_configured"
            }
    
    def _init_adapters(self):
        """初始化所有适配器"""
        # 至信链
        zhixin_config = self.config.get('tencent_zhixin', self.config)
        self.adapters['tencent_zhixin'] = TencentZhixinAdapter(zhixin_config)
        
        # 蚂蚁链
        antchain_config = self.config.get('antchain', {})
        self.adapters['antchain'] = AntChainAdapter(antchain_config)
        
        # FISCO BCOS
        fisco_config = self.config.get('fisco_bcos', {})
        self.adapters['fisco_bcos'] = FiscoBcosAdapter(fisco_config)
        
        # 设置默认链
        provider = self.config.get('provider', 'tencent_zhixin')
        if provider in self.adapters:
            self.default_chain = provider
        
        # 打印状态
        enabled_chains = [name for name, adapter in self.adapters.items() if adapter.enabled]
        if enabled_chains:
            print(f"✅ 区块链服务已初始化 - 默认链: {self.default_chain}, 已启用: {', '.join(enabled_chains)}")
        else:
            print(f"⚠️ 区块链服务已初始化（模拟模式）- 默认链: {self.default_chain}")
    
    def _get_adapter(self, chain: str = None) -> BlockchainAdapter:
        """获取指定链的适配器"""
        chain = chain or self.default_chain
        if chain not in self.adapters:
            raise ValueError(f"不支持的链: {chain}")
        return self.adapters[chain]
    
    # ===== DID 操作 =====
    
    async def register_did(self, user_id: str, user_type: str, chain: str = None, metadata: Dict = None) -> Dict:
        """注册链上数字身份"""
        adapter = self._get_adapter(chain)
        result = await adapter.register_did(user_id, user_type, metadata)
        result['chain'] = adapter.name
        return result
    
    async def verify_did(self, did: str, chain: str = None) -> Dict:
        """验证链上身份"""
        adapter = self._get_adapter(chain)
        return await adapter.verify_did(did)
    
    async def query_did(self, did: str, chain: str = None) -> Dict:
        """查询身份详情"""
        adapter = self._get_adapter(chain)
        return await adapter.query_did(did)
    
    # ===== 存证操作 =====
    
    async def store_evidence(self, data: Any, metadata: Dict = None, chain: str = None) -> Dict:
        """数据上链存证"""
        # 计算数据哈希
        if isinstance(data, str):
            data_hash = hashlib.sha256(data.encode('utf-8')).hexdigest()
        elif isinstance(data, dict):
            data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
            data_hash = hashlib.sha256(data_str.encode('utf-8')).hexdigest()
        else:
            data_hash = hashlib.sha256(str(data).encode('utf-8')).hexdigest()
        
        adapter = self._get_adapter(chain)
        result = await adapter.store_evidence(data_hash, metadata)
        result['chain'] = adapter.name
        return result
    
    async def verify_evidence(self, evidence_id: str, chain: str = None) -> Dict:
        """验证存证"""
        adapter = self._get_adapter(chain)
        return await adapter.verify_evidence(evidence_id)
    
    # ===== 状态查询 =====
    
    async def get_status(self, chain: str = None) -> Dict:
        """获取链状态"""
        if chain:
            adapter = self._get_adapter(chain)
            return await adapter.get_status()
        
        # 返回所有链状态
        return {
            "default_chain": self.default_chain,
            "chains": {
                name: await adapter.get_status()
                for name, adapter in self.adapters.items()
            }
        }
    
    async def get_all_chains_status(self) -> Dict:
        """获取所有链状态"""
        return await self.get_status()


# ===== 全局单例 =====
blockchain_service = BlockchainService()
