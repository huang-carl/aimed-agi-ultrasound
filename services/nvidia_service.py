"""
NVIDIA NIM 集成服务
支持阿里云百炼 + 英伟达双模型路由
"""

import os
import json
import requests
from typing import Dict, Any, Optional
from datetime import datetime

class NVIDIAClient:
    """NVIDIA NIM API 客户端"""
    
    def __init__(self):
        self.api_key = os.getenv("NVIDIA_API_KEY", "")
        self.api_base = "https://integrate.api.nvidia.com/v1"
        # 使用已验证可用的模型
        self.model = os.getenv("NVIDIA_MODEL", "meta/llama-3.3-70b-instruct")
        self.timeout = int(os.getenv("NVIDIA_TIMEOUT", "60"))
        
        if not self.api_key:
            raise ValueError("NVIDIA_API_KEY 未配置")
    
    def chat(self, messages: list, temperature: float = 0.7, max_tokens: int = 2000) -> Dict[str, Any]:
        """
        聊天接口
        
        Args:
            messages: 消息列表 [{"role": "user/system/assistant", "content": "..."}]
            temperature: 温度参数
            max_tokens: 最大输出 token 数
            
        Returns:
            响应结果
        """
        url = f"{self.api_base}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            return {
                "success": True,
                "content": result["choices"][0]["message"]["content"],
                "usage": result.get("usage", {}),
                "model": result.get("model", self.model)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": self.model
            }
    
    def diagnose(self, organ: str, image_description: str, context: str = "") -> Dict[str, Any]:
        """
        医疗诊断接口
        
        Args:
            organ: 器官类型
            image_description: 影像描述
            context: 额外上下文（病历等）
            
        Returns:
            诊断结果
        """
        system_prompt = """你是一名经验丰富的放射科医生，擅长超声影像诊断。
请根据提供的影像描述和病历信息，给出专业的诊断意见。
输出格式要求：
1. 诊断结论
2. 置信度（0-1 之间）
3. 鉴别诊断
4. 进一步检查建议
5. 治疗建议

请用中文回答。"""
        
        user_prompt = f"""
【检查部位】{organ}
【影像描述】{image_description}
"""
        
        if context:
            user_prompt += f"\n【病历信息】{context}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        result = self.chat(messages)
        
        if result["success"]:
            return {
                "success": True,
                "diagnosis": self._parse_diagnosis(result["content"]),
                "usage": result["usage"],
                "model": result["model"],
                "timestamp": datetime.now().isoformat(),
                "mode": "nvidia"
            }
        else:
            return {
                "success": False,
                "error": result["error"],
                "mode": "nvidia"
            }
    
    def _parse_diagnosis(self, text: str) -> Dict[str, Any]:
        """解析诊断结果"""
        # 简单解析，后续可用正则或 JSON 提取优化
        return {
            "raw_text": text,
            "disease": "待解析",
            "probability": 0.8,
            "suggestion": "请参考完整诊断文本"
        }


class DualModelService:
    """双模型路由服务（阿里云 + 英伟达）"""
    
    def __init__(self):
        self.routing_mode = os.getenv("MODEL_ROUTING", "smart")  # smart/nvidia/aliyun
        self.nvidia_client = NVIDIAClient() if os.getenv("NVIDIA_API_KEY") else None
        self.aliyun_client = self._init_aliyun()
    
    def _init_aliyun(self):
        """初始化阿里云客户端"""
        try:
            import dashscope
            from dashscope import Generation
            
            api_key = os.getenv("DASHSCOPE_API_KEY", "")
            if api_key:
                dashscope.api_key = api_key
                return {
                    "enabled": True,
                    "model": os.getenv("DASHSCOPE_MODEL", "qwen-plus")
                }
        except:
            pass
        return {"enabled": False}
    
    def diagnose(self, organ: str, image_description: str, context: str = "") -> Dict[str, Any]:
        """
        智能路由诊断
        
        Args:
            organ: 器官类型
            image_description: 影像描述
            context: 额外上下文
            
        Returns:
            诊断结果
        """
        # 计算上下文长度
        context_length = len(image_description) + len(context)
        
        # 智能路由逻辑
        if self.routing_mode == "nvidia":
            # 强制使用 NVIDIA
            return self._nvidia_diagnose(organ, image_description, context)
        elif self.routing_mode == "aliyun":
            # 强制使用阿里云
            return self._aliyun_diagnose(organ, image_description, context)
        else:
            # 智能路由：长文本用 NVIDIA，常规用阿里云
            if context_length > 50000 and self.nvidia_client:
                print(f"[路由] 长文本 ({context_length} chars) → NVIDIA")
                return self._nvidia_diagnose(organ, image_description, context)
            elif self.aliyun_client["enabled"]:
                print(f"[路由] 常规文本 → 阿里云 Qwen")
                return self._aliyun_diagnose(organ, image_description, context)
            elif self.nvidia_client:
                print(f"[路由] 阿里云不可用 → NVIDIA（降级）")
                return self._nvidia_diagnose(organ, image_description, context)
            else:
                return {
                    "success": False,
                    "error": "无可用模型服务",
                    "mode": "none"
                }
    
    def _nvidia_diagnose(self, organ: str, image_description: str, context: str) -> Dict[str, Any]:
        """NVIDIA 诊断"""
        if not self.nvidia_client:
            return {"success": False, "error": "NVIDIA 客户端未初始化"}
        return self.nvidia_client.diagnose(organ, image_description, context)
    
    def _aliyun_diagnose(self, organ: str, image_description: str, context: str) -> Dict[str, Any]:
        """阿里云诊断"""
        if not self.aliyun_client["enabled"]:
            return {"success": False, "error": "阿里云客户端未启用"}
        
        try:
            from dashscope import Generation
            
            system_prompt = """你是一名经验丰富的放射科医生，擅长超声影像诊断。
请根据提供的影像描述和病历信息，给出专业的诊断意见。
输出格式要求：
1. 诊断结论
2. 置信度（0-1 之间）
3. 鉴别诊断
4. 进一步检查建议
5. 治疗建议

请用中文回答。"""
            
            user_prompt = f"""
【检查部位】{organ}
【影像描述】{image_description}
"""
            if context:
                user_prompt += f"\n【病历信息】{context}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = Generation.call(
                model=self.aliyun_client["model"],
                messages=messages
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "diagnosis": {
                        "raw_text": response.output.text,
                        "disease": "待解析",
                        "probability": 0.8,
                        "suggestion": "请参考完整诊断文本"
                    },
                    "usage": response.usage if hasattr(response, 'usage') else {},
                    "model": self.aliyun_client["model"],
                    "timestamp": datetime.now().isoformat(),
                    "mode": "aliyun"
                }
            else:
                return {
                    "success": False,
                    "error": f"阿里云 API 错误：{response.code}",
                    "mode": "aliyun"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"阿里云诊断异常：{str(e)}",
                "mode": "aliyun"
            }


# 测试
if __name__ == "__main__":
    print("=" * 80)
    print("双模型服务测试")
    print("=" * 80)
    
    # 测试 NVIDIA
    if os.getenv("NVIDIA_API_KEY"):
        print("\n【NVIDIA 测试】")
        nvidia = NVIDIAClient()
        result = nvidia.diagnose("胃", "胃窦部黏膜充血水肿，可见点状糜烂")
        print(f"状态：{'✅ 成功' if result['success'] else '❌ 失败'}")
        if result['success']:
            print(f"模型：{result['model']}")
            print(f"诊断：{result['diagnosis']['raw_text'][:200]}...")
    else:
        print("\n⚠️ NVIDIA_API_KEY 未配置")
    
    print("\n" + "=" * 80)
