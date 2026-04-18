"""
诊断服务 - 支持真实 AI 调用和 Mock 模式切换
"""

import os
from typing import Dict, Any
from datetime import datetime
import dashscope
from dashscope import Generation

class DiagnosisService:
    """AI 诊断服务（支持 Mock/真实切换）"""
    
    def __init__(self):
        # 从环境变量读取配置
        self.api_key = os.getenv('DASHSCOPE_API_KEY', '')
        self.model = os.getenv('DASHSCOPE_MODEL', 'qwen-plus')
        self.mock_mode = os.getenv('MOCK_MODE', 'true').lower() == 'true'
        self.timeout = int(os.getenv('DIAGNOSIS_TIMEOUT', '30'))
        
        if not self.mock_mode and not self.api_key:
            raise ValueError("DASHSCOPE_API_KEY 未配置且 MOCK_MODE=false")
    
    def diagnose(self, organ: str, image_description: str) -> Dict[str, Any]:
        """
        诊断接口
        
        Args:
            organ: 器官类型（胃/胰腺）
            image_description: 影像描述
            
        Returns:
            诊断结果字典
        """
        if self.mock_mode:
            return self._mock_diagnose(organ, image_description)
        else:
            return self._real_diagnose(organ, image_description)
    
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
    
    def _real_diagnose(self, organ: str, image_description: str) -> Dict[str, Any]:
        """真实 AI 诊断（调用阿里云百炼）"""
        try:
            # 设置 API Key
            dashscope.api_key = self.api_key
            
            # 构建提示词
            prompt = self._build_prompt(organ, image_description)
            
            # 调用 DashScope API
            response = Generation.call(
                model=self.model,
                prompt=prompt,
                timeout=self.timeout
            )
            
            # 解析响应
            if response.status_code == 200:
                result = self._parse_ai_response(response.output.text, organ)
                result['timestamp'] = datetime.now().isoformat()
                result['mode'] = 'real'
                return result
            else:
                # API 调用失败，降级到 Mock
                print(f"DashScope API 调用失败：{response.code}, 降级到 Mock 模式")
                mock_result = self._mock_diagnose(organ, image_description)
                mock_result['mode'] = 'fallback'
                return mock_result
                
        except Exception as e:
            print(f"AI 诊断异常：{str(e)}, 降级到 Mock 模式")
            mock_result = self._mock_diagnose(organ, image_description)
            mock_result['mode'] = 'error_fallback'
            return mock_result
    
    def _build_prompt(self, organ: str, image_description: str) -> str:
        """构建 AI 提示词"""
        return f"""
你是一名经验丰富的超声诊断医生，请根据以下超声影像描述给出诊断意见：

【影像描述】
{image_description}

【诊断要求】
1. 判断器官：{organ}
2. 给出最可能的诊断
3. 评估置信度（0-1 之间）
4. 提供鉴别诊断建议
5. 给出进一步检查建议

【输出格式】
请严格按照以下 JSON 格式输出：
{{
  "organ": "{organ}",
  "disease": "诊断名称",
  "probability": 0.85,
  "suggestion": "建议内容",
  "image_quality": "good/fair/poor"
}}
"""
    
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
            except:
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
    service = DiagnosisService()
    result = service.diagnose('胃', '胃壁增厚，层次清晰')
    print(f"诊断结果：{result}")
    print(f"模式：{result['mode']}")
