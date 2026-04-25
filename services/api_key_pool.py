"""
API Key 智能降级服务
支持：多 Key 负载均衡、熔断机制、自动切换
"""

import os
import time
import random
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class KeyStatus(Enum):
    """Key 状态"""
    ACTIVE = "active"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class APIKey:
    """API Key 配置"""
    key: str
    provider: str  # dashscope / nvidia / zhipu / deepseek
    status: KeyStatus = KeyStatus.ACTIVE
    last_used: float = 0
    error_count: int = 0
    rate_limited_until: float = 0
    request_count: int = 0
    success_count: int = 0
    fail_count: int = 0
    avg_latency: float = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class APIKeyPool:
    """API Key 智能池"""
    
    def __init__(self, config_path: str = "./config/api_keys.json"):
        """
        初始化 Key 池
        
        Args:
            config_path: Key 配置文件路径
        """
        self.config_path = config_path
        self.keys: Dict[str, List[APIKey]] = {}
        self._load_config()
    
    def _load_config(self):
        """加载配置"""
        import json
        from dotenv import load_dotenv
        load_dotenv()  # 加载 .env 文件
        
        # 默认配置（从环境变量读取）
        default_config = {
            "dashscope": [
                {"key": os.getenv("DASHSCOPE_API_KEY", ""), "metadata": {"source": "primary"}}
            ],
            "nvidia": [
                {"key": os.getenv("NVIDIA_API_KEY", ""), "metadata": {"source": "primary"}}
            ],
            "zhipu": [
                {"key": os.getenv("ZHIPU_API_KEY", ""), "metadata": {"source": "backup"}}
            ],
            "deepseek": [
                {"key": os.getenv("DEEPSEEK_API_KEY", ""), "metadata": {"source": "backup"}}
            ]
        }
        
        # 尝试从文件加载
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                # 合并配置
                for provider, keys in config.items():
                    if provider not in default_config:
                        default_config[provider] = []
                    default_config[provider].extend(keys)
            except Exception as e:
                print(f"[KeyPool] 配置文件加载失败: {e}")
        
        # 解析配置
        for provider, key_configs in default_config.items():
            self.keys[provider] = []
            for kc in key_configs:
                if kc.get('key'):
                    self.keys[provider].append(APIKey(
                        key=kc['key'],
                        provider=provider,
                        metadata=kc.get('metadata', {})
                    ))
            
            if self.keys[provider]:
                print(f"[KeyPool] {provider}: {len(self.keys[provider])} 个 Key")
    
    def get_available_key(self, provider: str) -> Optional[APIKey]:
        """
        获取可用的 Key（负载均衡 + 状态检查）
        
        Args:
            provider: 提供商名称
            
        Returns:
            可用的 APIKey 或 None
        """
        if provider not in self.keys:
            return None
        
        now = time.time()
        available = []
        
        for key in self.keys[provider]:
            # 检查是否被禁用
            if key.status == KeyStatus.DISABLED:
                continue
            
            # 检查速率限制是否过期
            if key.status == KeyStatus.RATE_LIMITED:
                if now > key.rate_limited_until:
                    key.status = KeyStatus.ACTIVE
                    key.error_count = 0
                else:
                    continue
            
            # 检查错误计数（熔断）
            if key.error_count >= 5:
                key.status = KeyStatus.DISABLED
                print(f"[KeyPool] {provider} Key 熔断: {key.key[:20]}... (错误次数: {key.error_count})")
                continue
            
            available.append(key)
        
        if not available:
            print(f"[KeyPool] {provider}: 无可用 Key")
            return None
        
        # 负载均衡：选择使用次数最少的 Key
        available.sort(key=lambda k: k.request_count)
        selected = available[0]
        
        # 更新使用记录
        selected.last_used = now
        selected.request_count += 1
        
        return selected
    
    def record_success(self, key: APIKey, latency: float):
        """
        记录成功请求
        
        Args:
            key: API Key
            latency: 响应时间（秒）
        """
        key.success_count += 1
        key.error_count = max(0, key.error_count - 1)  # 逐步减少错误计数
        
        # 更新平均延迟
        if key.avg_latency == 0:
            key.avg_latency = latency
        else:
            key.avg_latency = key.avg_latency * 0.9 + latency * 0.1
        
        # 恢复正常状态
        if key.error_count < 3:
            key.status = KeyStatus.ACTIVE
    
    def record_failure(self, key: APIKey, error_type: str = "error"):
        """
        记录失败请求
        
        Args:
            key: API Key
            error_type: 错误类型（rate_limit / error）
        """
        key.fail_count += 1
        key.error_count += 1
        
        if error_type == "rate_limit":
            # 速率限制：冷却 60 秒
            key.status = KeyStatus.RATE_LIMITED
            key.rate_limited_until = time.time() + 60
            print(f"[KeyPool] {key.provider} Key 速率限制: {key.key[:20]}... (冷却 60s)")
        else:
            # 一般错误
            if key.error_count >= 5:
                key.status = KeyStatus.DISABLED
                print(f"[KeyPool] {key.provider} Key 熔断: {key.key[:20]}...")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = {}
        for provider, keys in self.keys.items():
            stats[provider] = {
                "total": len(keys),
                "active": sum(1 for k in keys if k.status == KeyStatus.ACTIVE),
                "rate_limited": sum(1 for k in keys if k.status == KeyStatus.RATE_LIMITED),
                "disabled": sum(1 for k in keys if k.status == KeyStatus.DISABLED),
                "total_requests": sum(k.request_count for k in keys),
                "success_rate": sum(k.success_count for k in keys) / max(1, sum(k.request_count for k in keys))
            }
        return stats
    
    def reset_all(self):
        """重置所有 Key 状态"""
        for provider, keys in self.keys.items():
            for key in keys:
                key.status = KeyStatus.ACTIVE
                key.error_count = 0
                key.rate_limited_until = 0
        print(f"[KeyPool] 所有 Key 已重置")


# 全局实例
_key_pool = None

def get_key_pool() -> APIKeyPool:
    """获取 Key 池实例"""
    global _key_pool
    if _key_pool is None:
        _key_pool = APIKeyPool()
    return _key_pool


# 测试
if __name__ == '__main__':
    print("=" * 60)
    print("API Key 智能降级服务测试")
    print("=" * 60)
    
    pool = get_key_pool()
    
    # 测试获取 Key
    for provider in ['dashscope', 'nvidia', 'zhipu', 'deepseek']:
        key = pool.get_available_key(provider)
        if key:
            print(f"✅ {provider}: {key.key[:20]}... (状态: {key.status.value})")
        else:
            print(f"❌ {provider}: 无可用 Key")
    
    # 测试统计
    print(f"\n统计: {pool.get_stats()}")
    
    print("=" * 60)
