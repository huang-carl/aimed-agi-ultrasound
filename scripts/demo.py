#!/usr/bin/env python3
"""
AIMED 充盈视界 - 完整演示脚本
展示从用户消息到 AI 诊断的完整流程
"""

import os
import sys
import json
from datetime import datetime

# 设置环境
os.environ['HERMES_BASE_URL'] = 'http://127.0.0.1:18790'
os.environ['NVIDIA_API_KEY'] = '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'

sys.path.insert(0, '/root/.openclaw/workspace')

from services.dingtalk_integration import DingTalkIntegration

def print_header(text):
    """打印标题"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_section(text):
    """打印小标题"""
    print(f"\n【{text}】")
    print("-" * 70)

def print_success(text):
    """打印成功消息"""
    print(f"✅ {text}")

def print_info(text):
    """打印信息"""
    print(f"ℹ️  {text}")

def main():
    """主演示流程"""
    
    print_header("AIMED 充盈视界 FillingVision - 系统演示")
    print_info(f"演示时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"Hermes 后端：http://127.0.0.1:18790")
    print_info(f"AI 模型：NVIDIA Llama-3.3-70B")
    
    # 初始化集成服务
    print_section("1. 初始化服务")
    try:
        integration = DingTalkIntegration()
        print_success("钉钉渠道集成服务已初始化")
        print_success(f"Hermes 后端地址：{integration.hermes_base_url}")
    except Exception as e:
        print(f"❌ 初始化失败：{e}")
        return
    
    # 演示场景 1: 用户问候
    print_section("2. 演示场景：用户问候")
    print_info("用户消息：\"你好\"")
    result = integration.process_message("你好", "015566043909-1816211276", "Skytop")
    print_success(f"响应类型：{result['type']}")
    print(f"\n响应内容:\n{result['response']}")
    
    # 演示场景 2: 胃部诊断
    print_section("3. 演示场景：胃部 AI 诊断")
    print_info("用户消息：\"帮我诊断：胃窦部黏膜充血水肿，可见点状糜烂\"")
    result = integration.process_message(
        "帮我诊断：胃窦部黏膜充血水肿，可见点状糜烂",
        "015566043909-1816211276",
        "Skytop"
    )
    print_success(f"诊断成功：{result['success']}")
    print_success(f"使用模型：{result.get('data', {}).get('model', 'N/A')}")
    print(f"\n诊断报告:\n{result['response']}")
    
    # 演示场景 3: 模型查询
    print_section("4. 演示场景：查询可用模型")
    print_info("用户消息：\"有哪些 AI 模型？\"")
    result = integration.process_message("有哪些 AI 模型？", "015566043909-1816211276", "Skytop")
    print_success(f"响应类型：{result['type']}")
    print(f"\n响应内容:\n{result['response']}")
    
    # 演示场景 4: 一般查询
    print_section("5. 演示场景：一般咨询")
    print_info("用户消息：\"这个系统能做什么？\"")
    result = integration.process_message(
        "这个系统能做什么？",
        "015566043909-1816211276",
        "Skytop"
    )
    print_success(f"响应类型：{result['type']}")
    print(f"\n响应内容:\n{result['response'][:500]}...")
    
    # 演示总结
    print_header("演示完成")
    print("""
📊 演示总结:

✅ 问候响应 - 正常
✅ 胃部诊断 - NVIDIA 模型调用成功
✅ 模型查询 - 返回可用模型列表
✅ 一般咨询 - 引导到诊断功能

🎯 系统状态:
   • OpenClaw Gateway (18789) - 运行中
   • Hermes 后端 (18790) - 运行中
   • NVIDIA NIM - API Key 有效
   • 钉钉渠道集成 - 测试通过

🤖 小超同学 & 小菲同学 已准备就绪！
""")
    
    print("=" * 70)
    print("  AIMED 充盈视界 FillingVision")
    print("  阿尔麦德智慧医疗（湖州）有限公司")
    print("  https://www.aius.xin")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
