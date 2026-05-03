"""
DashScope 诊断服务
通过阿里云百炼 (Qwen) 进行真实 AI 诊断
"""
import os
import json
import time
from typing import Dict, Any, Optional
from loguru import logger

try:
    import dashscope
    from dashscope import Generation
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False
    logger.warning("dashscope SDK 未安装，使用 HTTP 调用")


class DashScopeClient:
    """DashScope 客户端"""
    
    def __init__(self):
        self.api_key = os.getenv('DASHSCOPE_API_KEY', '')
        self.model = os.getenv('DASHSCOPE_MODEL', 'qwen3.5-plus')
        self.base_url = os.getenv('DASHSCOPE_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
        
        if DASHSCOPE_AVAILABLE and self.api_key:
            dashscope.api_key = self.api_key
            logger.info(f"DashScope SDK 已初始化 (模型: {self.model})")
        else:
            logger.info(f"DashScope HTTP 客户端已初始化 (模型: {self.model})")
    
    def diagnose(self, organ: str, image_description: str, context: str = "") -> Dict[str, Any]:
        """
        执行 AI 诊断
        
        Args:
            organ: 器官名称 (胃/胰腺)
            image_description: 影像描述
            context: 额外上下文（病历等）
        
        Returns:
            诊断结果字典
        """
        # 构建系统提示词
        system_prompt = f"""你是 AIMED 充盈视界 AI 诊断系统的{organ}专科诊断专家。

## 你的职责
根据患者影像描述和临床信息，提供专业诊断建议。

## 输出格式（JSON）
```json
{{
    "disease": "诊断结论",
    "probability": 0.85,
    "confidence": "high/medium/low",
    "findings": [
        {{
            "type": "发现类型",
            "location": "位置",
            "description": "详细描述",
            "confidence": 0.85
        }}
    ],
    "suggestion": "建议（如：建议结合临床症状，必要时行胃镜检查）",
    "risk_level": "low/medium/high",
    "next_steps": ["下一步检查建议"]
}}
```

## 注意事项
- 诊断结果必须基于医学证据
- 概率值范围 0.0-1.0
- 如果信息不足，请明确指出需要补充的信息
- 免责声明：本报告由 AI 辅助生成，仅供医生参考"""

        # 构建用户消息
        user_message = f"""器官：{organ}
影像描述：{image_description}
"""
        if context:
            user_message += f"\n临床信息：{context}"
        
        user_message += "\n请提供诊断分析。"
        
        try:
            if DASHSCOPE_AVAILABLE:
                return self._diagnose_sdk(system_prompt, user_message)
            else:
                return self._diagnose_http(system_prompt, user_message)
        except Exception as e:
            logger.error(f"DashScope 诊断失败：{e}")
            return {
                "success": False,
                "error": str(e),
                "fallback": True
            }
    
    def _diagnose_sdk(self, system_prompt: str, user_message: str) -> Dict[str, Any]:
        """使用 SDK 调用"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        response = Generation.call(
            model=self.model,
            messages=messages,
            result_format='message',
            temperature=0.3,
            max_tokens=2000
        )
        
        if response.status_code == 200:
            content = response.output.choices[0].message.content
            return self._parse_response(content)
        else:
            return {
                "success": False,
                "error": f"API 错误：{response.code} - {response.message}",
                "fallback": True
            }
    
    def _diagnose_http(self, system_prompt: str, user_message: str) -> Dict[str, Any]:
        """使用 HTTP 调用"""
        import requests
        
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.3,
            "max_tokens": 2000
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            return self._parse_response(content)
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}",
                "fallback": True
            }
    
    def _parse_response(self, content: str) -> Dict[str, Any]:
        """解析 AI 响应"""
        try:
            # 提取 JSON（可能包含在 markdown 代码块中）
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
                "model": self.model,
                "raw_text": content
            }
        except Exception as e:
            logger.error(f"解析 AI 响应失败：{e}")
            return {
                "success": False,
                "error": f"解析失败：{str(e)}",
                "raw_text": content,
                "fallback": True
            }


# 单例实例
dashscope_client = DashScopeClient()
