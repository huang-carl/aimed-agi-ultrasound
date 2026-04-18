#!/usr/bin/env python3
"""
真实诊断接口测试 - 使用阿里云百炼 API

使用方法：
    python scripts/test_real_diagnosis.py

前提条件：
    - .env 文件已配置 DASHSCOPE_API_KEY
    - 服务已启动（python main.py）
"""

import requests
from PIL import Image
import io
import sys

BASE_URL = "http://localhost:8000"

def create_test_image():
    """创建测试超声图像"""
    # 生成 512x512 灰度测试图（模拟超声影像）
    img = Image.new('L', (512, 512), color=128)
    
    # 添加一些噪声模拟真实超声
    import random
    pixels = img.load()
    for i in range(512):
        for j in range(512):
            pixels[i, j] = 128 + random.randint(-30, 30)
    
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def test_stomach_diagnosis():
    """测试胃诊断接口"""
    print("=" * 60)
    print("测试胃诊断接口")
    print("=" * 60)
    
    try:
        img_bytes = create_test_image()
        files = {"file": ("test_stomach.png", img_bytes, "image/png")}
        response = requests.post(
            f"{BASE_URL}/api/stomach/diagnose",
            files=files,
            timeout=30
        )
        
        print(f"状态码：{response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 诊断成功")
            print(f"   器官：{data.get('organ', 'N/A')}")
            print(f"   疾病：{data.get('disease', 'N/A')}")
            print(f"   置信度：{data.get('probability', 0):.2%}")
            print(f"   建议：{data.get('suggestion', 'N/A')}")
            print(f"   图像质量：{data.get('image_quality', 'N/A')}")
            return True
        else:
            print(f"❌ 诊断失败：{response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

def test_pancreas_diagnosis():
    """测试胰腺诊断接口"""
    print("\n" + "=" * 60)
    print("测试胰腺诊断接口")
    print("=" * 60)
    
    try:
        img_bytes = create_test_image()
        files = {"file": ("test_pancreas.png", img_bytes, "image/png")}
        response = requests.post(
            f"{BASE_URL}/api/pancreas/diagnose",
            files=files,
            timeout=30
        )
        
        print(f"状态码：{response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 诊断成功")
            print(f"   器官：{data.get('organ', 'N/A')}")
            print(f"   疾病：{data.get('disease', 'N/A')}")
            print(f"   置信度：{data.get('probability', 0):.2%}")
            print(f"   建议：{data.get('suggestion', 'N/A')}")
            print(f"   图像质量：{data.get('image_quality', 'N/A')}")
            return True
        else:
            print(f"❌ 诊断失败：{response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

def test_report_generation():
    """测试报告生成接口"""
    print("\n" + "=" * 60)
    print("测试报告生成接口")
    print("=" * 60)
    
    try:
        payload = {
            "patient_id": "TEST001",
            "patient_name": "测试患者",
            "diagnosis_results": [
                {
                    "organ": "胃",
                    "disease": "慢性胃炎",
                    "probability": 0.85,
                    "suggestion": "建议结合临床症状"
                },
                {
                    "organ": "胰腺",
                    "disease": "胰腺回声均匀",
                    "probability": 0.92,
                    "suggestion": "未见明显异常"
                }
            ],
            "doctor_id": "DR001",
            "doctor_name": "测试医生",
            "language": "zh"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/report/generate",
            json=payload,
            timeout=10
        )
        
        print(f"状态码：{response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 报告生成成功")
            print(f"   报告 ID: {data.get('report_id', 'N/A')}")
            print(f"   患者 ID: {data.get('patient_id', 'N/A')}")
            print(f"   状态：{data.get('status', 'N/A')}")
            return True
        else:
            print(f"❌ 报告生成失败：{response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

def main():
    """主测试流程"""
    print("\nAIMED Agent Swarm - 真实诊断接口测试")
    print(f"基础 URL: {BASE_URL}")
    print(f"测试时间：__import__('time').strftime('%Y-%m-%d %H:%M:%S')\n")
    
    # 检查服务连接
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ 服务可访问：{response.json()}\n")
        else:
            print(f"❌ 服务异常：{response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ 服务无法访问：{e}")
        sys.exit(1)
    
    # 运行测试
    results = []
    results.append(("胃诊断", test_stomach_diagnosis()))
    results.append(("胰腺诊断", test_pancreas_diagnosis()))
    results.append(("报告生成", test_report_generation()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    print()
    print(f"通过：{passed}/{total}")
    print(f"成功率：{passed/total*100:.1f}%")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1

if __name__ == "__main__":
    import time
    print(f"测试时间：{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    sys.exit(main())
