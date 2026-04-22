"""
诊断 API v1 测试脚本
测试双模型路由诊断服务
"""

import os
import sys
import requests
from datetime import datetime

# 设置环境变量
os.environ['NVIDIA_API_KEY'] = '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'
os.environ['MOCK_MODE'] = 'false'
os.environ['MODEL_ROUTING'] = 'smart'

BASE_URL = "http://127.0.0.1:18789"

print("=" * 70)
print("诊断 API v1 测试 - 双模型路由")
print("=" * 70)

# 测试 1: 获取可用模型
print("\n【测试 1】获取可用模型列表")
print("-" * 70)
try:
    response = requests.get(f"{BASE_URL}/api/v1/diagnosis/models", timeout=10)
    if response.status_code == 200:
        models = response.json()
        print(f"✅ 成功")
        print(f"   路由模式：{models.get('routing_mode', 'N/A')}")
        print(f"   Mock 模式：{models.get('mock_mode', 'N/A')}")
        print(f"   可用模型:")
        for model in models.get('models', []):
            print(f"      - {model['name']} ({model['provider']})")
    else:
        print(f"❌ 失败：{response.status_code}")
        print(f"   {response.text[:200]}")
except Exception as e:
    print(f"❌ 异常：{e}")
    print(f"   提示：请确保 Hermes 后端已启动 (python main.py)")

# 测试 2: 智能路由诊断
print("\n【测试 2】智能路由诊断")
print("-" * 70)
test_cases = [
    {
        "organ": "胃",
        "image_description": "胃窦部黏膜充血水肿，可见点状糜烂",
        "context": "患者有胃痛、反酸症状"
    },
    {
        "organ": "胰腺",
        "image_description": "胰腺体积增大，回声不均匀",
        "context": "患者有腹痛、恶心症状"
    }
]

for i, case in enumerate(test_cases, 1):
    print(f"\n   病例 {i}: {case['organ']}")
    try:
        payload = {
            "organ": case["organ"],
            "image_description": case["image_description"],
            "context": case["context"],
            "model_preference": "smart"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/diagnosis/diagnose",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 诊断成功")
            print(f"      模式：{result.get('mode', 'N/A')}")
            print(f"      模型：{result.get('model', 'N/A')}")
            print(f"      诊断：{result.get('disease', 'N/A')}")
            print(f"      置信度：{result.get('probability', 0)}")
            print(f"      建议：{result.get('suggestion', 'N/A')[:50]}...")
        else:
            print(f"   ❌ 失败：{response.status_code}")
            print(f"      {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ 异常：{e}")

# 测试 3: 强制使用 NVIDIA
print("\n【测试 3】强制使用 NVIDIA 模型")
print("-" * 70)
try:
    payload = {
        "organ": "胃",
        "image_description": "胃窦部黏膜充血水肿，可见点状糜烂",
        "context": "",
        "model_preference": "nvidia"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/diagnosis/diagnose",
        json=payload,
        timeout=60
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 诊断成功")
        print(f"   模式：{result.get('mode', 'N/A')}")
        print(f"   模型：{result.get('model', 'N/A')}")
        print(f"   诊断：{result.get('disease', 'N/A')}")
        print(f"   置信度：{result.get('probability', 0)}")
    else:
        print(f"❌ 失败：{response.status_code}")
except Exception as e:
    print(f"❌ 异常：{e}")

# 测试 4: 双模型对比（如果服务可用）
print("\n【测试 4】双模型对比诊断")
print("-" * 70)
try:
    payload = {
        "organ": "胃",
        "image_description": "胃窦部黏膜充血水肿，可见点状糜烂",
        "context": ""
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/diagnosis/compare",
        json=payload,
        timeout=120
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 对比成功")
        print(f"   任务 ID: {result.get('task_id', 'N/A')}")
        for r in result.get('results', []):
            print(f"   {r['provider']}: {r['disease']} (置信度：{r['probability']})")
    else:
        print(f"❌ 失败：{response.status_code}")
except Exception as e:
    print(f"❌ 异常：{e}")

print("\n" + "=" * 70)
print("测试完成！")
print("=" * 70)
print("\n💡 提示：如果看到大量异常，请先启动 Hermes 后端:")
print("   cd /root/.openclaw/workspace")
print("   python main.py")
print()
