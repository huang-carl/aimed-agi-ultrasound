"""
AI 诊断服务 - 多提供商支持
支持 DashScope / Zhipu / NVIDIA 自动切换
"""
import os
import json
from typing import Dict, Any, Optional
from loguru import logger
import requests


class AIDiagnosisService:
    """AI 诊断服务 - 多提供商自动切换"""
    
    def __init__(self):
        self.providers = []
        self._init_providers()
        logger.info(f"AI 诊断服务初始化完成，可用提供商: {[p['name'] for p in self.providers]}")
    
    def _init_providers(self):
        """初始化所有 AI 提供商"""
        
        # 1. DashScope (阿里云百炼) - Coding Plan 端点
        ds_key = os.getenv('DASHSCOPE_API_KEY', '')
        ds_base_url = os.getenv('DASHSCOPE_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
        if ds_key:
            self.providers.append({
                "name": "dashscope",
                "url": f"{ds_base_url}/chat/completions",
                "key": ds_key,
                "model": os.getenv('DASHSCOPE_MODEL', 'qwen-plus'),
                "priority": 1
            })
        
        # 2. Zhipu AI (智谱 - 永久免费)
        zhipu_key = os.getenv('ZHIPU_API_KEY', '')
        if zhipu_key:
            self.providers.append({
                "name": "zhipu",
                "url": f"{os.getenv('ZHIPU_BASE_URL', 'https://open.bigmodel.cn/api/paas/v4/')}/chat/completions",
                "key": zhipu_key,
                "model": "glm-4",
                "priority": 2
            })
        
        # 3. NVIDIA NIM (备用)
        nvidia_key = os.getenv('NVIDIA_API_KEY', '')
        if nvidia_key:
            self.providers.append({
                "name": "nvidia",
                "url": "https://integrate.api.nvidia.com/v1/chat/completions",
                "key": nvidia_key,
                "model": "meta/llama-3.3-70b-instruct",
                "priority": 3
            })
        
        # 按优先级排序
        self.providers.sort(key=lambda x: x['priority'])
    
    def diagnose(self, organ: str, image_description: str, context: str = "") -> Dict[str, Any]:
        """
        执行 AI 诊断（自动切换提供商）
        
        Args:
            organ: 器官名称
            image_description: 影像描述
            context: 临床上下文
        
        Returns:
            诊断结果
        """
        system_prompt = f"""你是 AIMED 充盈视界 AI 诊断系统的{organ}专科诊断专家。

## 职责
根据影像描述和临床信息，提供专业诊断建议。

## 输出格式（严格 JSON，不要包含其他文字）
{{
    "disease": "诊断结论",
    "probability": 0.85,
    "findings": [
        {{
            "type": "发现类型",
            "location": "位置",
            "description": "详细描述",
            "confidence": 0.85
        }}
    ],
    "suggestion": "建议",
    "risk_level": "low/medium/high"
}}

## 注意
- probability 范围 0.0-1.0
- 信息不足时明确指出
- 仅输出 JSON，不要其他文字"""

        user_message = f"器官：{organ}\n影像描述：{image_description}"
        if context:
            user_message += f"\n临床信息：{context}"
        user_message += "\n请提供诊断分析（仅 JSON）。"

        # 依次尝试每个提供商
        for provider in self.providers:
            try:
                logger.info(f"尝试 AI 提供商：{provider['name']} ({provider['model']})")
                result = self._call_api(provider, system_prompt, user_message)
                
                if result.get('success'):
                    result['provider'] = provider['name']
                    result['model'] = provider['model']
                    logger.info(f"✅ {provider['name']} 诊断成功")
                    return result
                else:
                    logger.warning(f"{provider['name']} 诊断失败：{result.get('error')}")
            except Exception as e:
                logger.error(f"{provider['name']} 异常：{e}")
        
        # 所有提供商都失败
        return {
            "success": False,
            "error": "所有 AI 提供商均不可用",
            "fallback": True
        }
    
    def _call_api(self, provider: Dict, system_prompt: str, user_message: str) -> Dict[str, Any]:
        """调用 API"""
        headers = {
            "Authorization": f"Bearer {provider['key']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": provider['model'],
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.3,
            "max_tokens": 2000
        }
        
        response = requests.post(
            provider['url'],
            json=payload,
            headers=headers,
            timeout=60  # Coding Plan 端点响应较慢，增加到 60 秒
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            return self._parse_response(content)
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}"
            }
    
    def _parse_response(self, content: str) -> Dict[str, Any]:
        """解析 AI 响应"""
        try:
            # 提取 JSON
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()
            
            result = json.loads(json_str)
            return {
                "success": True,
                "diagnosis": result,
                "raw_text": content
            }
        except Exception as e:
            logger.error(f"解析 AI 响应失败：{e}")
            return {
                "success": False,
                "error": f"解析失败：{str(e)}",
                "raw_text": content
            }


# 单例实例
ai_diagnosis_service = AIDiagnosisService()
