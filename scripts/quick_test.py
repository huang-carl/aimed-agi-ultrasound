#!/usr/bin/env python3
"""
快速测试脚本 - 验证服务基本功能

使用方法：
    python scripts/quick_test.py

前提条件：
    - 服务已启动（python main.py）
    - 依赖已安装（pip install -r requirements.txt）
"""

import requests
import sys
import time

BASE_URL = "http://localhost:8000"

def print_result(name, success, message=""):
    """打印测试结果"""
    status = "✅" if success else "❌"
    print(f"{status} {name}")
    if message:
        print(f"   {message}")

def test_health():
    """测试健康检查接口"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        success = response.status_code == 200
        data = response.json()
        print_result("健康检查", success, f"服务：{data.get('service', 'N/A')}")
        return success
    except Exception as e:
        print_result("健康检查", False, str(e))
        return False

def test_api_docs():
    """测试 API 文档可访问"""
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        success = response.status_code == 200
        print_result("API 文档", success, f"Swagger UI 可访问")
        return success
    except Exception as e:
        print_result("API 文档", False, str(e))
        return False

def test_stomach_diagnose():
    """测试胃诊断接口（需要测试图像）"""
    try:
        # 创建一个简单的测试图像
        from PIL import Image
        import io
        
        # 生成 512x512 灰度测试图
        img = Image.new('L', (512, 512), color=128)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        files = {"file": ("test_stomach.png", img_bytes, "image/png")}
        response = requests.post(
            f"{BASE_URL}/api/stomach/diagnose",
            files=files,
            timeout=30
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            print_result("胃诊断接口", success, 
                f"诊断：{data.get('disease', 'N/A')} (置信度：{data.get('probability', 0):.2%})")
        else:
            print_result("胃诊断接口", success, f"状态码：{response.status_code}")
        return success
    except Exception as e:
        print_result("胃诊断接口", False, str(e))
        return False

def test_pancreas_diagnose():
    """测试胰腺诊断接口"""
    try:
        from PIL import Image
        import io
        
        img = Image.new('L', (512, 512), color=128)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        files = {"file": ("test_pancreas.png", img_bytes, "image/png")}
        response = requests.post(
            f"{BASE_URL}/api/pancreas/diagnose",
            files=files,
            timeout=30
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            print_result("胰腺诊断接口", success,
                f"诊断：{data.get('disease', 'N/A')} (置信度：{data.get('probability', 0):.2%})")
        else:
            print_result("胰腺诊断接口", success, f"状态码：{response.status_code}")
        return success
    except Exception as e:
        print_result("胰腺诊断接口", False, str(e))
        return False

def test_conductor_dispatch():
    """测试总指挥任务分发接口"""
    try:
        payload = {
            "organs": ["stomach", "pancreas"],
            "image_paths": ["/tmp/test1.png", "/tmp/test2.png"],
            "patient_id": "TEST001"
        }
        response = requests.post(
            f"{BASE_URL}/api/conductor/dispatch",
            json=payload,
            timeout=10
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            print_result("总指挥任务分发", success,
                f"任务 ID: {data.get('task_id', 'N/A')}")
        else:
            print_result("总指挥任务分发", success, f"状态码：{response.status_code}")
        return success
    except Exception as e:
        print_result("总指挥任务分发", False, str(e))
        return False

def test_report_generate():
    """测试报告生成接口"""
    try:
        payload = {
            "patient_id": "TEST001",
            "patient_name": "测试患者",
            "diagnosis_results": [
                {
                    "organ": "胃",
                    "disease": "慢性胃炎",
                    "probability": 0.85,
                    "suggestion": "建议复查"
                }
            ],
            "doctor_id": "DR001",
            "doctor_name": "测试医生"
        }
        response = requests.post(
            f"{BASE_URL}/api/report/generate",
            json=payload,
            timeout=10
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            print_result("报告生成接口", success,
                f"报告 ID: {data.get('report_id', 'N/A')}")
        else:
            print_result("报告生成接口", success, f"状态码：{response.status_code}")
        return success
    except Exception as e:
        print_result("报告生成接口", False, str(e))
        return False

def test_api_v1():
    """测试 API v1 接口"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/conductor/task/test_task", timeout=5)
        # v1 接口可能返回 404（任务不存在），但接口本身应该可访问
        success = response.status_code in [200, 404]
        print_result("API v1 路由", success, f"状态码：{response.status_code}")
        return success
    except Exception as e:
        print_result("API v1 路由", False, str(e))
        return False

def main():
    """主测试流程"""
    print("=" * 60)
    print("AIMED Agent Swarm - 快速测试")
    print("=" * 60)
    print(f"基础 URL: {BASE_URL}")
    print(f"测试时间：{time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    # 检查服务是否可访问
    print("🔍 检查服务连接...")
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
        print("✅ 服务可访问\n")
    except:
        print("❌ 服务无法访问")
        print("\n请先启动服务：")
        print("  cd /root/.openclaw/workspace/github-aimed")
        print("  python main.py")
        sys.exit(1)
    
    # 运行所有测试
    results = []
    
    print("🧪 开始测试...\n")
    
    results.append(("健康检查", test_health()))
    results.append(("API 文档", test_api_docs()))
    results.append(("API v1 路由", test_api_v1()))
    results.append(("胃诊断接口", test_stomach_diagnose()))
    results.append(("胰腺诊断接口", test_pancreas_diagnose()))
    results.append(("总指挥任务分发", test_conductor_dispatch()))
    results.append(("报告生成接口", test_report_generate()))
    
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
    
    # 返回退出码
    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
