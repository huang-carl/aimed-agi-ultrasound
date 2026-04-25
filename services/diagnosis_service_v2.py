"""
诊断服务 V2 - 支持 API Key 智能降级 + 熔断机制
"""

import os
import time
import json
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from .api_key_pool import get_key_pool, KeyStatus
    KEY_POOL_AVAILABLE = True
except ImportError:
    KEY_POOL_AVAILABLE = False

try:
    import dashscope
    from dashscope import Generation
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False


class DiagnosisServiceV2:
    """AI 诊断服务 V2（支持智能降级 + 熔断）"""
    
    def __init__(self):
        self.key_pool = get_key_pool() if KEY_POOL_AVAILABLE else None
        self.mock_mode = os.getenv('MOCK_MODE', 'true').lower() == 'true'
        self.fallback_order = ['dashscope', 'nvidia', 'zhipu', 'deepseek']
        print(f"[DiagnosisV2] 初始化完成 - Key 池: {KEY_POOL_AVAILABLE}")
    
    def diagnose(self, organ: str, image_description: str, context: str = "", 
                 filling_status: str = "已充盈") -> Dict[str, Any]:
        """
        诊断接口（智能降级）
        """
        if filling_status != "已充盈":
            return {
                "success": False,
                "error": "未充盈状态下无法进行诊断",
                "mode": "rejected"
            }
        
        if self.mock_mode:
            return self._mock_diagnose(organ, image_description)
        
        # 尝试每个提供商
        for provider in self.fallback_order:
            try:
                result = self._try_provider(provider, organ, image_description, context)
                if result.get('success'):
                    return result
            except Exception as e:
                print(f"[DiagnosisV2] {provider} 失败: {e}")
                continue
        
        # 全部失败，降级到 Mock
        print(f"[DiagnosisV2] 所有提供商不可用，降级到 Mock")
        mock_result = self._mock_diagnose(organ, image_description)
        mock_result['mode'] = 'fallback'
        mock_result['error'] = '所有 AI 服务不可用'
        return mock_result
    
    def _try_provider(self, provider: str, organ: str, image_description: str, 
                      context: str) -> Dict[str, Any]:
        """尝试使用特定提供商"""
        if not self.key_pool:
            return {"success": False, "error": "Key 池不可用"}
        
        # 获取可用 Key
        key = self.key_pool.get_available_key(provider)
        if not key:
            return {"success": False, "error": f"{provider} 无可用 Key"}
        
        start_time = time.time()
        
        try:
            if provider == 'dashscope':
                result = self._dashscope_diagnose(key.key, organ, image_description, context)
            elif provider == 'nvidia':
                result = self._nvidia_diagnose(key.key, organ, image_description, context)
            elif provider == 'zhipu':
                result = self._zhipu_diagnose(key.key, organ, image_description, context)
            elif provider == 'deepseek':
                result = self._deepseek_diagnose(key.key, organ, image_description, context)
            else:
                return {"success": False, "error": f"未知提供商: {provider}"}
            
            latency = time.time() - start_time
            
            if result.get('success'):
                self.key_pool.record_success(key, latency)
                result['provider'] = provider
                result['latency'] = round(latency, 2)
                return result
            else:
                self.key_pool.record_failure(key, 'error')
                return result
                
        except Exception as e:
            latency = time.time() - start_time
            self.key_pool.record_failure(key, 'error')
            return {"success": False, "error": str(e)}
    
    def _dashscope_diagnose(self, api_key: str, organ: str, image_description: str, 
                           context: str) -> Dict[str, Any]:
        """阿里云诊断"""
        if not DASHSCOPE_AVAILABLE:
            return {"success": False, "error": "DashScope 库未安装"}
        
        try:
            dashscope.api_key = api_key
            
            prompt = self._build_prompt(organ, image_description, context)
            
            response = Generation.call(
                model='qwen3.5-plus',
                prompt=prompt,
                timeout=30
            )
            
            if response.status_code == 200:
                result = self._parse_response(response.output.text, organ)
                result['success'] = True
                result['model'] = 'qwen3.5-plus'
                return result
            else:
                return {"success": False, "error": f"API 错误: {response.code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _nvidia_diagnose(self, api_key: str, organ: str, image_description: str, 
                        context: str) -> Dict[str, Any]:
        """NVIDIA 诊断"""
        try:
            from openai import OpenAI
            
            client = OpenAI(
                api_key=api_key,
                base_url="https://integrate.api.nvidia.com/v1",
                timeout=60
            )
            
            prompt = self._build_prompt(organ, image_description, context)
            
            response = client.chat.completions.create(
                model="meta/llama-3.3-70b-instruct",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            
            result = self._parse_response(response.choices[0].message.content, organ)
            result['success'] = True
            result['model'] = 'meta/llama-3.3-70b-instruct'
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _zhipu_diagnose(self, api_key: str, organ: str, image_description: str, 
                       context: str) -> Dict[str, Any]:
        """智谱 AI 诊断"""
        try:
            from openai import OpenAI
            
            client = OpenAI(
                api_key=api_key,
                base_url="https://open.bigmodel.cn/api/paas/v4/",
                timeout=30
            )
            
            prompt = self._build_prompt(organ, image_description, context)
            
            response = client.chat.completions.create(
                model="glm-4-flash",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            
            result = self._parse_response(response.choices[0].message.content, organ)
            result['success'] = True
            result['model'] = 'glm-4-flash'
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _deepseek_diagnose(self, api_key: str, organ: str, image_description: str, 
                          context: str) -> Dict[str, Any]:
        """DeepSeek 诊断"""
        try:
            from openai import OpenAI
            
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com/v1",
                timeout=30
            )
            
            prompt = self._build_prompt(organ, image_description, context)
            
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            
            result = self._parse_response(response.choices[0].message.content, organ)
            result['success'] = True
            result['model'] = 'deepseek-chat'
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _mock_diagnose(self, organ: str, image_description: str) -> Dict[str, Any]:
        """Mock 诊断"""
        mock_results = {
            '胃': {
                'disease': '慢性胃炎',
                'probability': 0.85,
                'suggestion': '建议结合临床症状，必要时行胃镜检查'
            },
            '胰腺': {
                'disease': '胰腺回声均匀',
                'probability': 0.92,
                'suggestion': '未见明显异常，建议定期体检'
            }
        }
        
        result = mock_results.get(organ, mock_results['胃'])
        return {
            'organ': organ,
            'disease': result['disease'],
            'probability': result['probability'],
            'suggestion': result['suggestion'],
            'image_quality': 'good',
            'timestamp': datetime.now().isoformat(),
            'mode': 'mock',
            'success': True
        }
    
    def _build_prompt(self, organ: str, image_description: str, context: str = "") -> str:
        """构建提示词"""
        prompt = f"""你是一名经验丰富的超声诊断医生，请根据以下超声影像描述给出诊断意见：

【检查部位】
{organ}

【影像描述】
{image_description}
"""
        if context:
            prompt += f"""
【病历信息】
{context}
"""
        
        prompt += """
【诊断要求】
1. 给出最可能的诊断
2. 评估置信度（0-1 之间）
3. 提供鉴别诊断建议
4. 给出进一步检查建议

【输出格式】
请严格按照以下 JSON 格式输出：
{
  "organ": "器官名称",
  "disease": "诊断名称",
  "probability": 0.85,
  "suggestion": "建议内容",
  "image_quality": "good/fair/poor"
}
"""
        return prompt
    
    def _parse_response(self, text: str, organ: str) -> Dict[str, Any]:
        """解析响应"""
        import re
        
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group())
                return {
                    'organ': result.get('organ', organ),
                    'disease': result.get('disease', '未知'),
                    'probability': float(result.get('probability', 0.5)),
                    'suggestion': result.get('suggestion', '建议进一步检查'),
                    'image_quality': result.get('image_quality', 'fair'),
                    'success': True
                }
            except:
                pass
        
        return {
            'organ': organ,
            'disease': '待明确诊断',
            'probability': 0.5,
            'suggestion': '建议进一步检查',
            'image_quality': 'fair',
            'success': True
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.key_pool:
            return {"error": "Key 池不可用"}
        return self.key_pool.get_stats()


# 测试
if __name__ == '__main__':
    print("=" * 60)
    print("诊断服务 V2 测试")
    print("=" * 60)
    
    service = DiagnosisServiceV2()
    
    # 测试 Mock 模式
    print("\n【测试 1】Mock 模式")
    result = service.diagnose('胃', '胃窦部黏膜充血水肿')
    print(f"模式: {result.get('mode')}")
    print(f"诊断: {result.get('disease')}")
    
    # 测试智能降级
    print("\n【测试 2】智能降级")
    os.environ['MOCK_MODE'] = 'false'
    service.mock_mode = False
    result = service.diagnose('胃', '胃窦部黏膜充血水肿，可见点状糜烂')
    print(f"提供商: {result.get('provider', 'N/A')}")
    print(f"模型: {result.get('model', 'N/A')}")
    print(f"诊断: {result.get('disease')}")
    print(f"延迟: {result.get('latency', 'N/A')}s")
    
    # 统计
    print(f"\n统计: {service.get_stats()}")
    
    print("=" * 60)
