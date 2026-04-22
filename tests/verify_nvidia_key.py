"""
NVIDIA API Key 验证脚本
"""

import os
import requests
import json
from datetime import datetime

def verify_api_key():
    """验证 NVIDIA API Key"""
    
    api_key = os.getenv("NVIDIA_API_KEY", "")
    
    if not api_key:
        print("❌ NVIDIA_API_KEY 未配置")
        return False
    
    # 测试连接
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "meta/llama-3.3-70b-instruct",
        "messages": [
            {"role": "user", "content": "Hello, this is a test."}
        ],
        "max_tokens": 10
    }
    
    print(f"🔍 正在验证 API Key...")
    print(f"   模型：meta/llama-3.3-70b-instruct")
    print(f"   端点：{url}")
    print()
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"📊 响应状态码：{response.status_code}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API Key 有效！")
            print()
            print(f"   响应模型：{result.get('model', 'N/A')}")
            print(f"   完成时间：{datetime.now().isoformat()}")
            print(f"   测试输出：{result['choices'][0]['message']['content']}")
            return True
            
        elif response.status_code == 401:
            print("❌ 鉴权失败 (401)")
            print("   可能原因：API Key 无效或已过期")
            return False
            
        elif response.status_code == 403:
            print("❌ 权限不足 (403)")
            print("   可能原因：API Key 有效但无此模型访问权限")
            return False
            
        elif response.status_code == 429:
            print("⚠️  请求频率限制 (429)")
            print("   API Key 有效，但请求过于频繁")
            return True
            
        else:
            print(f"❌ 未知错误 ({response.status_code})")
            print(f"   响应：{response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except Exception as e:
        print(f"❌ 连接异常：{str(e)}")
        return False


def check_model_availability(api_key: str, model: str) -> bool:
    """检查特定模型是否可用"""
    
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "test"}],
        "max_tokens": 5
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        return response.status_code in [200, 429]  # 429 也算可用（只是限流）
    except:
        return False


def list_available_models(api_key: str):
    """列出常用模型并检查可用性"""
    
    models = [
        "meta/llama-3.3-70b-instruct",
        "meta/llama-3.1-405b-instruct",
        "meta/llama-3.1-70b-instruct",
        "meta/llama-3-70b-instruct",
        "google/gemma-2b",
        "google/gemma-7b",
        "mistralai/mistral-large",
        "mistralai/mixtral-8x7b-instruct-v0.1",
    ]
    
    print("\n📋 模型可用性检查：")
    print("-" * 60)
    
    for model in models:
        available = check_model_availability(api_key, model)
        status = "✅" if available else "❌"
        print(f"   {status} {model}")
    
    print("-" * 60)


if __name__ == "__main__":
    print("=" * 60)
    print("NVIDIA API Key 验证工具")
    print("=" * 60)
    print()
    
    success = verify_api_key()
    
    if success:
        api_key = os.getenv("NVIDIA_API_KEY", "")
        list_available_models(api_key)
    
    print()
    print("=" * 60)
