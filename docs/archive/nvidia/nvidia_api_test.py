#!/usr/bin/env python3
"""
NVIDIA NIM API 测试脚本
用于验证 API Key 有效性和模型中文能力
"""

import os
import json
import requests
from typing import Dict, Any

# 配置
NVIDIA_API_KEY = "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"
NVIDIA_API_BASE = "https://integrate.api.nvidia.com/v1"

# 测试模型列表
TEST_MODELS = [
    "nvidia/nemotron-3-super-120b",  # 1M 上下文，推荐
    "nvidia/nemotron-plus-405b",     # 405B 参数，最强推理
    "meta/llama-3.3-70b-instruct",   # Llama 3.3
    "qwen/qwen-2.5-coder-32b-instruct",  # 中文代码模型
]

def test_nvidia_api(model: str, prompt: str) -> Dict[str, Any]:
    """
    测试 NVIDIA NIM API
    
    Args:
        model: 模型名称
        prompt: 测试提示词
        
    Returns:
        响应结果
    """
    url = f"{NVIDIA_API_BASE}/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "你是一名专业的医疗助手，请用中文回答用户的问题。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return {
            "success": True,
            "model": model,
            "response": result["choices"][0]["message"]["content"],
            "usage": result.get("usage", {}),
            "status_code": response.status_code
        }
        
    except requests.exceptions.HTTPError as e:
        return {
            "success": False,
            "model": model,
            "error": f"HTTP 错误：{e.response.status_code} - {e.response.text}",
            "status_code": e.response.status_code
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "model": model,
            "error": f"请求错误：{str(e)}",
            "status_code": 0
        }
    except Exception as e:
        return {
            "success": False,
            "model": model,
            "error": f"未知错误：{str(e)}",
            "status_code": 0
        }


def run_tests():
    """运行所有测试"""
    
    # 医疗场景测试用例
    test_cases = [
        {
            "name": "基础对话",
            "prompt": "你好，请介绍一下你自己。"
        },
        {
            "name": "医学术语理解",
            "prompt": "请解释一下'慢性胃炎伴糜烂'是什么意思？有哪些典型症状？"
        },
        {
            "name": "诊断建议",
            "prompt": "患者主诉：上腹部疼痛 3 天，伴有反酸、嗳气。胃镜检查显示胃窦部黏膜充血水肿，可见点状糜烂。请给出诊断意见和治疗建议。"
        },
        {
            "name": "长文本理解",
            "prompt": "请分析以下病历并给出诊断建议：\n\n患者，男性，45 岁，公司职员。\n主诉：反复上腹部隐痛 6 个月，加重 2 周。\n现病史：患者 6 个月前无明显诱因出现上腹部隐痛，呈持续性，与进食无关，伴有反酸、嗳气、腹胀。自行服用'奥美拉唑'后症状可缓解。2 周前上述症状加重，疼痛频率增加，伴有食欲减退、乏力。发病以来，患者精神尚可，睡眠欠佳，大小便正常，体重无明显变化。\n既往史：否认高血压、糖尿病、冠心病病史。否认肝炎、结核等传染病史。否认手术、外伤史。否认药物、食物过敏史。\n个人史：吸烟史 20 年，每日 10-15 支。偶有饮酒。\n家族史：父亲患胃癌（已故），母亲健在。\n体格检查：T 36.5℃，P 80 次/分，R 18 次/分，BP 120/80mmHg。神志清楚，精神可。全身皮肤黏膜无黄染，全身浅表淋巴结未触及肿大。心肺查体无异常。腹平软，上腹部轻压痛，无反跳痛及肌紧张，肝脾肋下未触及，墨菲氏征阴性，肠鸣音正常，4 次/分。\n辅助检查：胃镜（2024-01-15）：胃窦部黏膜充血水肿，可见点状糜烂，幽门螺杆菌检测阳性。"
        }
    ]
    
    print("=" * 80)
    print("NVIDIA NIM API 测试报告")
    print("=" * 80)
    print(f"API Key: {NVIDIA_API_KEY[:20]}...")
    print(f"测试时间：{__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 测试每个模型
    for model in TEST_MODELS:
        print(f"\n{'='*80}")
        print(f"测试模型：{model}")
        print("=" * 80)
        
        for test_case in test_cases:
            print(f"\n【测试用例】{test_case['name']}")
            print(f"【提示词】{test_case['prompt'][:100]}..." if len(test_case['prompt']) > 100 else f"【提示词】{test_case['prompt']}")
            
            result = test_nvidia_api(model, test_case['prompt'])
            
            if result['success']:
                print(f"✅ 状态码：{result['status_code']}")
                print(f"✅ 响应：{result['response'][:200]}..." if len(result['response']) > 200 else f"✅ 响应：{result['response']}")
                if 'usage' in result:
                    print(f"✅ Token 使用：{result['usage']}")
            else:
                print(f"❌ 错误：{result['error']}")
            
            print("-" * 80)
    
    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)


if __name__ == "__main__":
    run_tests()
