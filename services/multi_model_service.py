"""
多模型路由服务 - AIMED 胃胰腺超声造影 AI 诊断
支持：阿里云百炼 + 智谱 AI + DeepSeek + NVIDIA NIM
"""

import os
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()


class ModelClient:
    """通用模型客户端"""
    
    def __init__(self, name: str, api_key: str, base_url: str, model: str, timeout: int = 60):
        self.name = name
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        self.client = self._init_client()
    
    def _init_client(self):
        """初始化 OpenAI 兼容客户端"""
        try:
            from openai import OpenAI
            return OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout
            )
        except Exception as e:
            print(f"[{self.name}] 客户端初始化失败：{str(e)}")
            return None
    
    def chat(self, messages: list, temperature: float = 0.7, max_tokens: int = 2000) -> Dict[str, Any]:
        """
        聊天接口
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大输出 token 数
            
        Returns:
            响应结果
        """
        if not self.client:
            return {"success": False, "error": f"{self.name} 客户端未初始化"}
        
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            elapsed = time.time() - start_time
            
            return {
                "success": True,
                "content": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "elapsed_time": round(elapsed, 2),
                "finish_reason": response.choices[0].finish_reason
            }
            
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "elapsed_time": round(elapsed, 2),
                "model": self.model
            }
    
    def diagnose(self, organ: str, image_description: str, context: str = "") -> Dict[str, Any]:
        """
        医疗诊断接口
        
        Args:
            organ: 器官类型（胃/胰腺）
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
        
        user_prompt = f"""【检查部位】{organ}
【影像描述】{image_description}"""
        
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
                "diagnosis": {
                    "raw_text": result["content"],
                    "organ": organ,
                    "model": result["model"],
                    "timestamp": datetime.now().isoformat()
                },
                "usage": result["usage"],
                "elapsed_time": result["elapsed_time"],
                "mode": self.name
            }
        else:
            return {
                "success": False,
                "error": result["error"],
                "mode": self.name
            }


class MultiModelRouter:
    """多模型智能路由"""
    
    def __init__(self):
        self.routing_mode = os.getenv("MODEL_ROUTING", "smart")
        self.context_threshold = int(os.getenv("CONTEXT_LENGTH_THRESHOLD", "30000"))
        
        # 初始化各模型客户端
        self.clients = {}
        self._init_clients()
    
    def _init_clients(self):
        """初始化所有模型客户端"""
        
        # 阿里云百炼（主力 - Coding Plan）
        aliyun_key = os.getenv("DASHSCOPE_API_KEY", "")
        if aliyun_key:
            self.clients["aliyun"] = ModelClient(
                name="阿里云百炼",
                api_key=aliyun_key,
                base_url=os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
                model=os.getenv("DASHSCOPE_MODEL", "qwen3.5-plus")
            )
            print(f"[路由] 阿里云百炼已启用：{self.clients['aliyun'].model}")
        
        # 智谱 AI（辅助 - 永久免费）
        zhipu_key = os.getenv("ZHIPU_API_KEY", "")
        if zhipu_key:
            self.clients["zhipu"] = ModelClient(
                name="智谱 AI",
                api_key=zhipu_key,
                base_url=os.getenv("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/"),
                model=os.getenv("ZHIPU_MODEL", "glm-4-flash")
            )
            print(f"[路由] 智谱 AI 已启用：{self.clients['zhipu'].model}")
        
        # DeepSeek（主力 - 永久免费额度）
        deepseek_key = os.getenv("DEEPSEEK_API_KEY", "")
        if deepseek_key:
            self.clients["deepseek"] = ModelClient(
                name="DeepSeek",
                api_key=deepseek_key,
                base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
                model=os.getenv("DEEPSEEK_MODEL", "deepseek-v3.2")
            )
            print(f"[路由] DeepSeek 已启用：{self.clients['deepseek'].model}")
        
        # NVIDIA NIM（复杂推理 - 免费一年）
        nvidia_key = os.getenv("NVIDIA_API_KEY", "")
        if nvidia_key:
            self.clients["nvidia"] = ModelClient(
                name="NVIDIA NIM",
                api_key=nvidia_key,
                base_url=os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"),
                model=os.getenv("NVIDIA_MODEL", "meta/llama-3.3-70b-instruct"),
                timeout=int(os.getenv("NVIDIA_TIMEOUT", "60"))
            )
            print(f"[路由] NVIDIA NIM 已启用：{self.clients['nvidia'].model}")
        
        if not self.clients:
            print("[路由] ⚠️ 无可用模型服务")
    
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
        
        # 根据路由模式选择模型
        if self.routing_mode == "nvidia":
            selected = "nvidia"
        elif self.routing_mode == "aliyun":
            selected = "aliyun"
        elif self.routing_mode == "zhipu":
            selected = "zhipu"
        elif self.routing_mode == "kimi":
            selected = "kimi"
        else:
            # 智能路由
            selected = self._smart_select(context_length)
        
        # 执行诊断
        if selected in self.clients:
            print(f"[路由] 选择模型：{selected}（上下文长度：{context_length}）")
            return self.clients[selected].diagnose(organ, image_description, context)
        else:
            # 降级：尝试其他可用模型
            for fallback in ["aliyun", "deepseek", "zhipu", "nvidia"]:
                if fallback in self.clients:
                    print(f"[路由] 降级：{selected} 不可用，使用 {fallback}")
                    return self.clients[fallback].diagnose(organ, image_description, context)
            
            return {
                "success": False,
                "error": "无可用模型服务",
                "mode": "none"
            }
    
    def _smart_select(self, context_length: int) -> str:
        """
        智能选择模型（四模型路由策略）
        
        策略：
        1. 有阿里云 → 阿里云百炼（主力，Coding Plan 免费额度）
        2. 有 DeepSeek → DeepSeek（主力，永久免费额度）
        3. 有智谱 → 智谱 AI（辅助，永久免费）
        4. 有 NVIDIA → NVIDIA NIM（备用，复杂推理）
        """
        # 优先级：阿里云 > DeepSeek > 智谱 > NVIDIA
        if "aliyun" in self.clients:
            return "aliyun"
        elif "deepseek" in self.clients:
            return "deepseek"
        elif "zhipu" in self.clients:
            return "zhipu"
        elif "nvidia" in self.clients:
            return "nvidia"
        else:
            return "none"
    
    def get_status(self) -> Dict[str, Any]:
        """获取所有模型状态"""
        status = {
            "routing_mode": self.routing_mode,
            "context_threshold": self.context_threshold,
            "available_models": list(self.clients.keys()),
            "models": {}
        }
        
        for name, client in self.clients.items():
            status["models"][name] = {
                "model": client.model,
                "base_url": client.base_url,
                "status": "✅ 可用" if client.client else "❌ 不可用"
            }
        
        return status


# 全局路由实例
router = MultiModelRouter()


def diagnose(organ: str, image_description: str, context: str = "") -> Dict[str, Any]:
    """诊断接口（兼容旧版）"""
    return router.diagnose(organ, image_description, context)


# 测试
if __name__ == "__main__":
    print("=" * 80)
    print("多模型路由服务测试")
    print("=" * 80)
    
    # 获取状态
    status = router.get_status()
    print(f"\n路由模式：{status['routing_mode']}")
    print(f"可用模型：{', '.join(status['available_models'])}")
    print()
    
    for name, info in status['models'].items():
        print(f"  {name}: {info['model']} - {info['status']}")
    
    # 测试诊断
    print("\n" + "=" * 80)
    print("测试诊断")
    print("=" * 80)
    
    result = router.diagnose(
        organ="胃",
        image_description="胃窦部黏膜充血水肿，可见点状糜烂，蠕动正常",
        context="患者，男，45 岁，上腹隐痛 3 个月，反酸嗳气"
    )
    
    if result["success"]:
        print(f"\n✅ 诊断成功")
        print(f"模型：{result['mode']}")
        print(f"耗时：{result['elapsed_time']}s")
        print(f"Token：{result['usage']}")
        print(f"\n诊断结果：")
        print(result['diagnosis']['raw_text'][:300] + "...")
    else:
        print(f"\n❌ 诊断失败：{result['error']}")
