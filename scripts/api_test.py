#!/usr/bin/env python3
"""
Hermes 后端 API 测试脚本

用法：
    python3 scripts/api_test.py
"""

import requests
import sys
from datetime import datetime

BASE_URL = "http://localhost:18795"

def print_section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_health():
    """测试健康检查接口"""
    print_section("1. 健康检查")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"状态码：{response.status_code}")
        print(f"响应：{response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

def test_stomach_health():
    """测试胃诊断健康检查"""
    print_section("2. 胃诊断接口健康检查")
    
    try:
        response = requests.get(f"{BASE_URL}/api/stomach/health", timeout=5)
        print(f"状态码：{response.status_code}")
        print(f"响应：{response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

def test_pancreas_health():
    """测试胰腺诊断健康检查"""
    print_section("3. 胰腺诊断接口健康检查")
    
    try:
        response = requests.get(f"{BASE_URL}/api/pancreas/health", timeout=5)
        print(f"状态码：{response.status_code}")
        print(f"响应：{response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

def test_report_health():
    """测试报告生成健康检查"""
    print_section("4. 报告生成接口健康检查")
    
    try:
        response = requests.get(f"{BASE_URL}/api/report/health", timeout=5)
        print(f"状态码：{response.status_code}")
        print(f"响应：{response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

def test_conductor_health():
    """测试总指挥接口健康检查"""
    print_section("5. 总指挥接口健康检查")
    
    try:
        response = requests.get(f"{BASE_URL}/api/conductor/health", timeout=5)
        print(f"状态码：{response.status_code}")
        print(f"响应：{response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

def test_demo_page():
    """测试 Demo 页面"""
    print_section("6. Demo 演示页面")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"状态码：{response.status_code}")
        print(f"页面标题：{'AIMED 充盈视界' if response.status_code == 200 else 'N/A'}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

def main():
    """运行所有测试"""
    print(f"\n🧪 Hermes 后端 API 测试")
    print(f"时间：{datetime.now().isoformat()}")
    print(f"基础 URL: {BASE_URL}")
    
    results = {
        "健康检查": test_health(),
        "胃诊断": test_stomach_health(),
        "胰腺诊断": test_pancreas_health(),
        "报告生成": test_report_health(),
        "总指挥": test_conductor_health(),
        "Demo 页面": test_demo_page(),
    }
    
    print_section("测试结果汇总")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")
    
    print(f"\n总计：{passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
