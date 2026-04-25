"""
统一模型路由服务
为 OpenClaw 和 Hermes 提供统一的智能路由
"""

import os
import time
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


@dataclass
class ModelProvider:
    """模型提供商配置"""
    name: str
    api_key: str
    base_url: str
    models: List[str]
    default_model: str
    timeout: int = 30
    priority: int = 999  # 数字越小优先级越高
    status: str = "active"  # active/rate_limited/error/disabled
    error_count: int = 0
    rate_limited_until: float = 0
    request_count: int = 0
    success_count: int = 0
    fail_count: int = 0
    avg_latency: float = 0


class ModelRouter:
    """统一模型路由"""
    
    def __init__(self, config_path: str = "/root/.openclaw/openclaw.json"):
        """
        初始化路由
        
        Args:
            config_path: OpenClaw 配置文件路径
        """
        self.config_path = config_path
        self.providers: Dict[str, ModelProvider] = {}
        self.client_cache: Dict[str, OpenAI] = {}
        self._load_config()
    
    def _load_config(self):
        """加载配置"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            providers = config.get('models', {}).get('providers', {})
            
            # 定义优先级
            priority_map = {
                'dashscope': 1,
                'nvidia': 2,
                'deepseek': 3,
                'zhipu': 4
            }
            
            for name, pconfig in providers.items():
                models = pconfig.get('models', [])
                if not models:
                    continue
                
                model_ids = [m['id'] for m in models]
                default_model = models[0]['id']
                
                self.providers[name] = ModelProvider(
                    name=name,
                    api_key=pconfig.get('apiKey', ''),
                    base_url=pconfig.get('baseUrl', ''),
                    models=model_ids,
                    default_model=default_model,
                    timeout=pconfig.get('timeout', 30),
                    priority=priority_map.get(name, 999)
                )
                
                print(f"[Router] {name}: {len(model_ids)} 个模型 (优先级: {priority_map.get(name, 999)})")
            
            # 按优先级排序
            self.ordered_providers = sorted(
                self.providers.values(),
                key=lambda p: p.priority
            )
            
        except Exception as e:
            print(f"[Router] 配置加载失败: {e}")
    
    def _get_client(self, provider: ModelProvider) -> Optional[OpenAI]:
        """获取或创建 OpenAI 客户端"""
        if provider.name in self.client_cache:
            return self.client_cache[provider.name]
        
        if not OPENAI_AVAILABLE:
            return None
        
        try:
            client = OpenAI(
                api_key=provider.api_key,
                base_url=provider.base_url,
                timeout=provider.timeout
            )
            self.client_cache[provider.name] = client
            return client
        except Exception as e:
            print(f"[Router] 客户端创建失败 ({provider.name}): {e}")
            return None
    
    def chat(self, messages: List[Dict], model: Optional[str] = None,
             temperature: float = 0.7, max_tokens: int = 2000) -> Dict[str, Any]:
        """
        智能聊天（自动降级）
        
        Args:
            messages: 消息列表
            model: 指定模型（可选）
            temperature: 温度参数
            max_tokens: 最大输出 token 数
            
        Returns:
            响应结果
        """
        # 确定提供商顺序
        if model:
            # 指定模型：查找对应提供商
            target_provider = None
            for p in self.providers.values():
                if model in p.models:
                    target_provider = p
                    break
            
            if target_provider:
                providers_to_try = [target_provider]
            else:
                providers_to_try = self.ordered_providers
        else:
            # 未指定模型：按优先级尝试
            providers_to_try = self.ordered_providers
        
        # 尝试每个提供商
        for provider in providers_to_try:
            if not self._is_available(provider):
                continue
            
            try:
                result = self._try_provider(provider, messages, model, temperature, max_tokens)
                if result.get('success'):
                    return result
            except Exception as e:
                print(f"[Router] {provider.name} 失败: {e}")
                self._record_failure(provider)
                continue
        
        # 全部失败
        return {
            'success': False,
            'error': '所有模型提供商不可用',
            'providers_tried': len(providers_to_try)
        }
    
    def _is_available(self, provider: ModelProvider) -> bool:
        """检查提供商是否可用"""
        if provider.status == 'disabled':
            return False
        
        if provider.status == 'rate_limited':
            if time.time() > provider.rate_limited_until:
                provider.status = 'active'
                provider.error_count = 0
                return True
            return False
        
        if provider.error_count >= 5:
            provider.status = 'disabled'
            print(f"[Router] {provider.name} 熔断 (错误次数: {provider.error_count})")
            return False
        
        return True
    
    def _try_provider(self, provider: ModelProvider, messages: List[Dict],
                     model: Optional[str], temperature: float, max_tokens: int) -> Dict[str, Any]:
        """尝试使用特定提供商"""
        client = self._get_client(provider)
        if not client:
            return {'success': False, 'error': '客户端不可用'}
        
        start_time = time.time()
        target_model = model or provider.default_model
        
        try:
            response = client.chat.completions.create(
                model=target_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            latency = time.time() - start_time
            
            # 记录成功
            provider.request_count += 1
            provider.success_count += 1
            provider.error_count = max(0, provider.error_count - 1)
            if provider.avg_latency == 0:
                provider.avg_latency = latency
            else:
                provider.avg_latency = provider.avg_latency * 0.9 + latency * 0.1
            
            return {
                'success': True,
                'content': response.choices[0].message.content,
                'model': response.model,
                'provider': provider.name,
                'latency': round(latency, 2),
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            }
            
        except Exception as e:
            latency = time.time() - start_time
            self._record_failure(provider)
            return {'success': False, 'error': str(e)}
    
    def _record_failure(self, provider: ModelProvider):
        """记录失败"""
        provider.request_count += 1
        provider.fail_count += 1
        provider.error_count += 1
        
        if 'rate limit' in str(provider.error_count).lower() or '429' in str(provider.error_count):
            provider.status = 'rate_limited'
            provider.rate_limited_until = time.time() + 60
            print(f"[Router] {provider.name} 速率限制 (冷却 60s)")
        elif provider.error_count >= 5:
            provider.status = 'disabled'
            print(f"[Router] {provider.name} 熔断")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = {}
        for name, provider in self.providers.items():
            stats[name] = {
                'status': provider.status,
                'models': provider.models,
                'priority': provider.priority,
                'requests': provider.request_count,
                'success': provider.success_count,
                'failures': provider.fail_count,
                'errors': provider.error_count,
                'avg_latency': round(provider.avg_latency, 2)
            }
        return stats
    
    def reset_all(self):
        """重置所有提供商状态"""
        for provider in self.providers.values():
            provider.status = 'active'
            provider.error_count = 0
            provider.rate_limited_until = 0
        print(f"[Router] 所有提供商已重置")


# 全局实例
_router = None

def get_router() -> ModelRouter:
    """获取路由实例"""
    global _router
    if _router is None:
        _router = ModelRouter()
    return _router


# 测试
if __name__ == '__main__':
    print("=" * 60)
    print("统一模型路由测试")
    print("=" * 60)
    
    router = get_router()
    
    # 测试聊天
    print("\n【测试 1】智能聊天（默认模型）")
    result = router.chat([
        {"role": "user", "content": "你好，请用一句话介绍自己"}
    ])
    print(f"提供商: {result.get('provider', 'N/A')}")
    print(f"模型: {result.get('model', 'N/A')}")
    print(f"延迟: {result.get('latency', 'N/A')}s")
    print(f"内容: {result.get('content', 'N/A')[:100]}...")
    
    # 测试指定模型
    print("\n【测试 2】指定模型")
    result = router.chat([
        {"role": "user", "content": "你好"}
    ], model='glm-4-flash')
    print(f"提供商: {result.get('provider', 'N/A')}")
    print(f"模型: {result.get('model', 'N/A')}")
    print(f"延迟: {result.get('latency', 'N/A')}s")
    
    # 统计
    print(f"\n统计: {json.dumps(router.get_stats(), indent=2, ensure_ascii=False)}")
    
    print("=" * 60)
