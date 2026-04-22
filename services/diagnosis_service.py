"""
诊断服务 - 支持阿里云 + 英伟达双模型路由 + Mock 模式
"""

import os
from typing import Dict, Any
from datetime import datetime
import dashscope
from dashscope import Generation

# 导入 NVIDIA 服务
try:
    from .nvidia_service import DualModelService
    NVIDIA_AVAILABLE = True
except:
    NVIDIA_AVAILABLE = False

class DiagnosisService:
    """AI 诊断服务（支持阿里云 + 英伟达双模型路由 + Mock 模式）"""
    
    def __init__(self):
        # 从环境变量读取配置
        self.api_key = os.getenv('DASHSCOPE_API_KEY', '')
        self.model = os.getenv('DASHSCOPE_MODEL', 'qwen-plus')
        self.mock_mode = os.getenv('MOCK_MODE', 'true').lower() == 'true'
        self.timeout = int(os.getenv('DIAGNOSIS_TIMEOUT', '30'))
        
        # 模型路由策略
        self.routing_mode = os.getenv('MODEL_ROUTING', 'smart')  # smart/aliyun/nvidia
        
        # 初始化 NVIDIA 服务
        self.nvidia_service = None
        if NVIDIA_AVAILABLE and os.getenv('NVIDIA_API_KEY'):
            try:
                self.nvidia_service = DualModelService()
            except Exception as e:
                print(f"NVIDIA 服务初始化失败：{e}")
        
        if not self.mock_mode and not self.api_key and not self.nvidia_service:
            raise ValueError("无可用 AI 服务：DASHSCOPE_API_KEY 和 NVIDIA_API_KEY 均未配置且 MOCK_MODE=false")
    
    def diagnose(self, organ: str, image_description: str, context: str = "", filling_status: str = "已充盈") -> Dict[str, Any]:
        """
        诊断接口（支持双模型路由）
        
        Args:
            organ: 器官类型（胃/胰腺）
            image_description: 影像描述
            context: 额外上下文（病历等）
            filling_status: 充盈状态（必须为"已充盈"）
            
        Returns:
            诊断结果字典
        """
        # 检查充盈状态 - 只接受充盈状态
        if filling_status != "已充盈":
            return {
                "success": False,
                "error": "未充盈状态下无法进行诊断，请口服造影剂后重新检查",
                "mode": "rejected"
            }
        
        if self.mock_mode:
            return self._mock_diagnose(organ, image_description)
        else:
            return self._smart_diagnose(organ, image_description, context)
    
    def _mock_diagnose(self, organ: str, image_description: str) -> Dict[str, Any]:
        """Mock 诊断（演示/测试用）"""
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
            'mode': 'mock'
        }
    
    def _smart_diagnose(self, organ: str, image_description: str, context: str = "") -> Dict[str, Any]:
        """智能路由诊断（阿里云 + 英伟达）"""
        
        # 计算上下文长度
        context_length = len(image_description) + len(context)
        
        # 路由决策
        if self.routing_mode == 'nvidia' and self.nvidia_service:
            print(f"[路由] 强制使用 NVIDIA")
            return self._nvidia_diagnose(organ, image_description, context)
        elif self.routing_mode == 'aliyun' and self.api_key:
            print(f"[路由] 强制使用阿里云")
            return self._aliyun_diagnose(organ, image_description, context)
        elif self.routing_mode == 'smart':
            # 智能路由：长文本用 NVIDIA，常规用阿里云
            if context_length > 50000 and self.nvidia_service:
                print(f"[路由] 长文本 ({context_length} chars) → NVIDIA")
                return self._nvidia_diagnose(organ, image_description, context)
            elif self.api_key:
                print(f"[路由] 常规文本 → 阿里云 Qwen")
                return self._aliyun_diagnose(organ, image_description, context)
            elif self.nvidia_service:
                print(f"[路由] 阿里云不可用 → NVIDIA（降级）")
                return self._nvidia_diagnose(organ, image_description, context)
        
        # 无可用服务，降级到 Mock
        print(f"[路由] 无可用 AI 服务 → Mock（降级）")
        mock_result = self._mock_diagnose(organ, image_description)
        mock_result['mode'] = 'fallback'
        return mock_result
    
    def _nvidia_diagnose(self, organ: str, image_description: str, context: str) -> Dict[str, Any]:
        """NVIDIA 诊断"""
        if not self.nvidia_service:
            print("NVIDIA 服务不可用，降级到 Mock")
            return self._mock_diagnose(organ, image_description)
        
        result = self.nvidia_service.diagnose(organ, image_description, context)
        
        if result.get('success'):
            return {
                'organ': organ,
                'disease': result['diagnosis'].get('disease', '待解析'),
                'probability': result['diagnosis'].get('probability', 0.8),
                'suggestion': result['diagnosis'].get('suggestion', '请参考完整诊断'),
                'image_quality': 'good',
                'raw_text': result['diagnosis'].get('raw_text', ''),
                'timestamp': datetime.now().isoformat(),
                'mode': 'nvidia',
                'model': result.get('model', 'meta/llama-3.3-70b-instruct'),
                'usage': result.get('usage', {})
            }
        else:
            print(f"NVIDIA 诊断失败：{result.get('error')}, 降级到 Mock")
            mock_result = self._mock_diagnose(organ, image_description)
            mock_result['mode'] = 'nvidia_fallback'
            return mock_result
    
    def _aliyun_diagnose(self, organ: str, image_description: str, context: str) -> Dict[str, Any]:
        """阿里云诊断"""
        if not self.api_key:
            print("阿里云 API Key 未配置，降级到 Mock")
            return self._mock_diagnose(organ, image_description)
        
        try:
            # 设置 API Key
            dashscope.api_key = self.api_key
            
            # 构建提示词
            prompt = self._build_prompt(organ, image_description, context)
            
            # 调用 DashScope API
            response = Generation.call(
                model=self.model,
                prompt=prompt,
                timeout=self.timeout
            )
            
            # 解析响应
            if response.status_code == 200:
                result = self._parse_ai_response(response.output.text, organ)
                result['raw_text'] = response.output.text
                result['timestamp'] = datetime.now().isoformat()
                result['mode'] = 'aliyun'
                result['model'] = self.model
                result['usage'] = response.usage if hasattr(response, 'usage') else {}
                return result
            else:
                print(f"阿里云 API 失败：{response.code}, 降级到 Mock")
                mock_result = self._mock_diagnose(organ, image_description)
                mock_result['mode'] = 'aliyun_fallback'
                return mock_result
                
        except Exception as e:
            print(f"阿里云诊断异常：{str(e)}, 降级到 Mock")
            mock_result = self._mock_diagnose(organ, image_description)
            mock_result['mode'] = 'aliyun_error'
            return mock_result
    
    def _build_prompt(self, organ: str, image_description: str, context: str = "") -> str:
        """构建 AI 提示词"""
        prompt = f"""
你是一名经验丰富的超声诊断医生，请根据以下超声影像描述给出诊断意见：

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
    
    def _parse_ai_response(self, text: str, organ: str) -> Dict[str, Any]:
        """解析 AI 响应"""
        import json
        import re
        
        # 提取 JSON 部分
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group())
                return {
                    'organ': result.get('organ', organ),
                    'disease': result.get('disease', '未知'),
                    'probability': float(result.get('probability', 0.5)),
                    'suggestion': result.get('suggestion', '建议进一步检查'),
                    'image_quality': result.get('image_quality', 'fair')
                }
            except Exception as e:
                print(f"JSON 解析失败：{e}")
                pass
        
        # 解析失败，返回默认结果
        return {
            'organ': organ,
            'disease': '待明确诊断',
            'probability': 0.5,
            'suggestion': '建议进一步检查',
            'image_quality': 'fair'
        }

# 测试
if __name__ == '__main__':
    print("=" * 60)
    print("诊断服务测试 - 双模型路由")
    print("=" * 60)
    
    service = DiagnosisService()
    
    # 测试 1: Mock 模式
    print("\n【测试 1】Mock 模式")
    os.environ['MOCK_MODE'] = 'true'
    service.mock_mode = True
    result = service.diagnose('胃', '胃壁增厚，层次清晰')
    print(f"模式：{result['mode']}")
    print(f"诊断：{result['disease']}")
    
    # 测试 2: 真实模式（智能路由）
    print("\n【测试 2】智能路由模式")
    os.environ['MOCK_MODE'] = 'false'
    os.environ['MODEL_ROUTING'] = 'smart'
    service.mock_mode = False
    service.routing_mode = 'smart'
    result = service.diagnose('胃', '胃窦部黏膜充血水肿，可见点状糜烂')
    print(f"模式：{result['mode']}")
    print(f"模型：{result.get('model', 'N/A')}")
    print(f"诊断：{result['disease']}")
    print(f"置信度：{result['probability']}")
    
    print("\n" + "=" * 60)
