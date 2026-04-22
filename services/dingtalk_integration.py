"""
钉钉渠道集成服务 - 将钉钉消息路由到 Hermes 后端
"""

import os
import json
import requests
from typing import Dict, Any, Optional
from datetime import datetime

class DingTalkIntegration:
    """钉钉渠道集成服务"""
    
    def __init__(self):
        self.hermes_base_url = os.getenv("HERMES_BASE_URL", "http://127.0.0.1:18790")
        self.diagnosis_endpoint = f"{self.hermes_base_url}/api/v1/diagnosis/diagnose"
        self.models_endpoint = f"{self.hermes_base_url}/api/v1/diagnosis/models"
        self.timeout = int(os.getenv("HERMES_TIMEOUT", "60"))
        
        # 小超同学配置
        self.agent_name = "小超同学"
        self.agent_emoji = "🤖"
    
    def process_message(self, message: str, sender_id: str, sender_name: str = "") -> Dict[str, Any]:
        """
        处理钉钉消息
        
        Args:
            message: 用户消息内容
            sender_id: 发送者 ID
            sender_name: 发送者名称
            
        Returns:
            响应结果
        """
        # 判断消息类型
        if "诊断" in message or "检查" in message or "影像" in message:
            return self._handle_diagnosis_request(message, sender_id, sender_name)
        elif "模型" in message or "能力" in message:
            return self._handle_models_request()
        elif "你好" in message or "在吗" in message or "hello" in message.lower():
            return self._handle_greeting(sender_name)
        else:
            return self._handle_general_query(message, sender_id, sender_name)
    
    def _handle_diagnosis_request(self, message: str, sender_id: str, sender_name: str) -> Dict[str, Any]:
        """处理诊断请求"""
        # 简单解析消息，提取器官和影像描述
        organ = self._extract_organ(message)
        image_description = self._extract_image_description(message)
        
        if not organ or not image_description:
            return {
                "success": True,
                "response": self._build_help_message(),
                "type": "text"
            }
        
        # 调用 Hermes 诊断 API
        try:
            payload = {
                "organ": organ,
                "image_description": image_description,
                "context": f"用户：{sender_name or sender_id}",
                "model_preference": "nvidia"
            }
            
            response = requests.post(
                self.diagnosis_endpoint,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": self._format_diagnosis_result(result),
                    "type": "markdown",
                    "data": result
                }
            else:
                return {
                    "success": False,
                    "response": f"⚠️ 诊断服务暂时不可用，请稍后重试\n错误码：{response.status_code}",
                    "type": "text"
                }
                
        except Exception as e:
            return {
                "success": False,
                "response": f"⚠️ 系统异常：{str(e)}",
                "type": "text"
            }
    
    def _handle_models_request(self) -> Dict[str, Any]:
        """处理模型查询请求"""
        try:
            response = requests.get(self.models_endpoint, timeout=10)
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": self._format_models_info(result),
                    "type": "markdown"
                }
            else:
                return {
                    "success": False,
                    "response": "⚠️ 模型信息服务暂时不可用",
                    "type": "text"
                }
        except Exception as e:
            return {
                "success": False,
                "response": f"⚠️ 系统异常：{str(e)}",
                "type": "text"
            }
    
    def _handle_greeting(self, sender_name: str) -> Dict[str, Any]:
        """处理问候消息"""
        name = sender_name or "您"
        return {
            "success": True,
            "response": f"""👋 您好，{name}！

我是{self.agent_emoji} **{self.agent_name}**，您的 AI 医疗助手。

**我可以帮您：**
- 🏥 超声影像诊断（胃/胰腺）
- 📊 检查报告解读
- 💡 医疗咨询建议

**使用示例：**
- "帮我诊断一下：胃窦部黏膜充血水肿"
- "胰腺体积增大，回声不均匀，是什么问题？"

有什么可以帮您的吗？😊""",
            "type": "markdown"
        }
    
    def _handle_general_query(self, message: str, sender_id: str, sender_name: str) -> Dict[str, Any]:
        """处理一般查询"""
        return {
            "success": True,
            "response": f"""🤔 我收到您的消息了：

"{message}"

我是{self.agent_emoji} **{self.agent_name}**，主要负责**超声影像诊断**服务。

**我可以帮您：**
- 🏥 胃/胰腺超声造影 AI 诊断
- 📊 检查报告解读
- 💡 相关医疗咨询

**试试这样说：**
- "帮我诊断：胃窦部黏膜充血水肿，可见点状糜烂"
- "胰腺体积增大，回声不均匀，有什么问题？"

有什么可以帮您的吗？😊""",
            "type": "markdown"
        }
    
    def _extract_organ(self, message: str) -> Optional[str]:
        """从消息中提取器官类型"""
        organ_keywords = {
            "胃": ["胃", "胃部", "胃窦", "胃体", "胃底"],
            "胰腺": ["胰腺", "胰头", "胰体", "胰尾"]
        }
        
        for organ, keywords in organ_keywords.items():
            for keyword in keywords:
                if keyword in message:
                    return organ
        
        return None
    
    def _extract_image_description(self, message: str) -> Optional[str]:
        """从消息中提取影像描述"""
        # 简单实现：提取冒号后的内容或整个消息
        if "：" in message:
            parts = message.split("：", 1)
            if len(parts) > 1:
                desc = parts[1].strip()
                if len(desc) > 5:
                    return desc
        elif ":" in message:
            parts = message.split(":", 1)
            if len(parts) > 1:
                desc = parts[1].strip()
                if len(desc) > 5:
                    return desc
        
        # 如果没有冒号或冒号后内容太短，返回整个消息
        if len(message) > 10:
            return message
        
        return None
    
    def _build_help_message(self) -> str:
        """构建帮助消息"""
        return f"""🏥 **{self.agent_name} 诊断助手**

请提供以下信息：
1. **检查部位**：胃 或 胰腺
2. **影像描述**：超声检查所见

**使用示例：**
- "帮我诊断：胃窦部黏膜充血水肿，可见点状糜烂"
- "胰腺：体积增大，回声不均匀"
- "胃部检查：胃壁增厚，层次清晰"

有什么可以帮您的吗？😊"""
    
    def _format_diagnosis_result(self, result: Dict[str, Any]) -> str:
        """格式化诊断结果"""
        if not result.get('success'):
            return f"⚠️ 诊断失败：{result.get('suggestion', '未知错误')}"
        
        disease = result.get('disease', '待明确')
        probability = result.get('probability', 0)
        suggestion = result.get('suggestion', '建议进一步检查')
        mode = result.get('mode', 'unknown')
        model = result.get('model', '')
        raw_text = result.get('raw_text', '')
        
        # 构建 Markdown 响应
        response = f"""🏥 **AI 诊断报告**

📋 **诊断结论**
{disease}

📊 **置信度**
{probability:.0%}

💡 **建议**
{suggestion}

---
🤖 模型：{model or mode}
⏰ 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

        # 如果有详细诊断文本，附加到后面
        if raw_text and len(raw_text) > 50:
            response += f"""

📝 **详细诊断**
{raw_text[:1000]}{'...' if len(raw_text) > 1000 else ''}"""

        response += f"""

---
⚠️ **免责声明**：本结果仅供参考，不能替代专业医生诊断。请以医院正式检查报告为准。"""
        
        return response
    
    def _format_models_info(self, result: Dict[str, Any]) -> str:
        """格式化模型信息"""
        models = result.get('models', [])
        routing_mode = result.get('routing_mode', 'smart')
        
        models_text = "\n".join([
            f"- **{m['name']}** ({m['provider']})\n  上下文：{m.get('context_length', 'N/A')}"
            for m in models
        ])
        
        return f"""🤖 **可用 AI 模型**

{models_text}

📡 路由模式：{routing_mode}

---
{self.agent_emoji} {self.agent_name} 为您服务"""


# 测试
if __name__ == "__main__":
    integration = DingTalkIntegration()
    
    print("=" * 60)
    print("钉钉渠道集成测试")
    print("=" * 60)
    
    # 测试问候
    print("\n【测试 1】问候")
    result = integration.process_message("你好", "test_user", "测试用户")
    print(f"类型：{result['type']}")
    print(f"响应：{result['response'][:200]}...")
    
    # 测试诊断
    print("\n【测试 2】诊断请求")
    result = integration.process_message(
        "帮我诊断：胃窦部黏膜充血水肿，可见点状糜烂",
        "test_user",
        "测试用户"
    )
    print(f"成功：{result['success']}")
    print(f"类型：{result['type']}")
    if result['success']:
        print(f"响应：{result['response'][:300]}...")
    else:
        print(f"错误：{result['response']}")
    
    print("\n" + "=" * 60)
