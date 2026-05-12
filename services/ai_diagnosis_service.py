"""
AI 诊断服务 - 直接调用大模型 API
"""

import os
import time
import json
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class AIDiagnosisService:
    """AI 诊断服务（多模型 API 调用）"""
    
    def __init__(self):
        self.dashscope_api_key = os.getenv('DASHSCOPE_API_KEY', '')
        self.dashscope_model = os.getenv('DASHSCOPE_MODEL', 'qwen3.5-plus')
        self.dashscope_base_url = os.getenv('DASHSCOPE_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
        
        self.zhipu_api_key = os.getenv('ZHIPU_API_KEY', '')
        self.zhipu_model = os.getenv('ZHIPU_MODEL', 'glm-4-flash')
        self.zhipu_base_url = os.getenv('ZHIPU_BASE_URL', 'https://open.bigmodel.cn/api/paas/v4/')
        
        self.deepseek_api_key = os.getenv('DEEPSEEK_API_KEY', '')
        self.deepseek_model = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
        self.deepseek_base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')
        
        # 初始化 API 客户端
        self.clients = {}
        if self.dashscope_api_key and OPENAI_AVAILABLE:
            self.clients['dashscope'] = OpenAI(
                api_key=self.dashscope_api_key,
                base_url=self.dashscope_base_url
            )
            logger.info(f"DashScope 客户端已初始化 (模型: {self.dashscope_model})")
        
        if self.zhipu_api_key and OPENAI_AVAILABLE:
            self.clients['zhipu'] = OpenAI(
                api_key=self.zhipu_api_key,
                base_url=self.zhipu_base_url
            )
            logger.info(f"智谱 AI 客户端已初始化 (模型: {self.zhipu_model})")
        
        if self.deepseek_api_key and OPENAI_AVAILABLE:
            self.clients['deepseek'] = OpenAI(
                api_key=self.deepseek_api_key,
                base_url=self.deepseek_base_url
            )
            logger.info(f"DeepSeek 客户端已初始化 (模型: {self.deepseek_model})")
        
        self.fallback_order = ['dashscope', 'zhipu', 'deepseek']
    
    def diagnose(self, organ: str, image_description: str, context: str = "") -> Dict[str, Any]:
        """
        执行 AI 诊断
        
        Args:
            organ: 器官名称（胃/胰腺）
            image_description: 影像描述
            context: 临床上下文
        
        Returns:
            诊断结果
        """
        # 尝试每个提供商
        for provider in self.fallback_order:
            try:
                if provider not in self.clients:
                    continue
                result = self._call_api(provider, organ, image_description, context)
                if result.get('success'):
                    return result
            except Exception as e:
                logger.warning(f"[{provider}] 诊断失败: {e}")
                continue
        
        # 全部失败
        return {
            'success': False,
            'error': '所有 AI 服务不可用',
            'diagnosis': None
        }
    
    def _call_api(self, provider: str, organ: str, image_description: str, context: str) -> Dict[str, Any]:
        """调用特定提供商的 API"""
        client = self.clients[provider]
        model = self._get_model_name(provider)
        
        # 构建提示词
        prompt = self._build_prompt(organ, image_description, context)
        
        start_time = time.time()
        
        # 调用 API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一名经验丰富的超声诊断医生。请根据以下超声影像描述给出诊断意见。必须使用 JSON 格式输出。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000,
            timeout=30
        )
        
        latency = time.time() - start_time
        
        # 解析响应
        result_text = response.choices[0].message.content
        diagnosis = self._parse_response(result_text, organ)
        
        return {
            'success': True,
            'provider': provider,
            'model': model,
            'latency': round(latency, 2),
            'diagnosis': diagnosis
        }
    
    def _get_model_name(self, provider: str) -> str:
        """获取模型名称"""
        models = {
            'dashscope': self.dashscope_model,
            'zhipu': self.zhipu_model,
            'deepseek': self.deepseek_model
        }
        return models.get(provider, 'unknown')
    
    def _build_prompt(self, organ: str, image_description: str, context: str = "") -> str:
        """构建诊断提示词"""
        organ_info = {
            '胃': {
                'focus': '胃壁层次结构、黏膜状态、病变特征、Su-RADS 分级',
                'common_diseases': '慢性胃炎、胃溃疡、胃息肉、胃癌'
            },
            '胰腺': {
                'focus': '胰腺实质回声、导管结构、占位病变、Pa-RADS 分级',
                'common_diseases': '胰腺炎、胰腺囊肿、胰腺癌'
            }
        }
        
        info = organ_info.get(organ, {
            'focus': '器官结构、病变特征',
            'common_diseases': '待明确诊断'
        })
        
        prompt = f"""【检查部位】{organ}

【影像描述】
{image_description}
"""
        if context:
            prompt += f"""
【病历信息】
{context}
"""
        
        prompt += f"""
【诊断要求】
1. 重点关注：{info['focus']}
2. 常见疾病：{info['common_diseases']}
3. 给出最可能的诊断
4. 评估置信度（0-1 之间）
5. 提供鉴别诊断建议
6. 给出进一步检查建议

【输出格式】
请严格按照以下 JSON 格式输出：
{{
  "organ": "器官名称",
  "disease": "诊断名称",
  "probability": 0.85,
  "suggestion": "建议内容",
  "image_quality": "good/fair/poor",
  "differential_diagnosis": "鉴别诊断",
  "next_steps": "下一步建议"
}}
"""
        return prompt
    
    def _parse_response(self, text: str, organ: str) -> Dict[str, Any]:
        """解析 API 响应"""
        import re
        
        # 尝试提取 JSON
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group())
                return {
                    'organ': result.get('organ', organ),
                    'disease': result.get('disease', '待明确诊断'),
                    'probability': float(result.get('probability', 0.5)),
                    'suggestion': result.get('suggestion', '建议进一步检查'),
                    'image_quality': result.get('image_quality', 'fair'),
                    'differential_diagnosis': result.get('differential_diagnosis', ''),
                    'next_steps': result.get('next_steps', '')
                }
            except:
                pass
        
        # 如果解析失败，返回默认结果
        return {
            'organ': organ,
            'disease': '待明确诊断',
            'probability': 0.5,
            'suggestion': '建议进一步检查',
            'image_quality': 'fair',
            'differential_diagnosis': '',
            'next_steps': ''
        }


# 全局实例
ai_diagnosis_service = AIDiagnosisService()
