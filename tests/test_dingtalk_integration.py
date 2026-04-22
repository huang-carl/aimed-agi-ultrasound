"""
钉钉渠道集成测试
"""

import os
import sys

# 设置环境变量
os.environ['HERMES_BASE_URL'] = 'http://127.0.0.1:18790'
os.environ['HERMES_TIMEOUT'] = '60'

print("=" * 70)
print("钉钉渠道集成测试 - 小超同学")
print("=" * 70)

from services.dingtalk_integration import DingTalkIntegration

integration = DingTalkIntegration()

# 测试 1: 问候
print("\n【测试 1】问候消息")
print("-" * 70)
result = integration.process_message("你好", "015566043909-1816211276", "Skytop")
print(f"✅ 类型：{result['type']}")
print(f"✅ 响应长度：{len(result['response'])} 字符")
print(f"\n响应预览:")
print(result['response'][:300])

# 测试 2: 诊断请求 - 胃
print("\n\n【测试 2】胃部诊断请求")
print("-" * 70)
result = integration.process_message(
    "帮我诊断：胃窦部黏膜充血水肿，可见点状糜烂",
    "015566043909-1816211276",
    "Skytop"
)
print(f"✅ 成功：{result['success']}")
print(f"✅ 类型：{result['type']}")
if result['success']:
    print(f"\n诊断响应:")
    print(result['response'][:500])
else:
    print(f"❌ 错误：{result['response']}")

# 测试 3: 诊断请求 - 胰腺
print("\n\n【测试 3】胰腺诊断请求")
print("-" * 70)
result = integration.process_message(
    "胰腺：体积增大，回声不均匀",
    "015566043909-1816211276",
    "Skytop"
)
print(f"✅ 成功：{result['success']}")
print(f"✅ 类型：{result['type']}")
if result['success']:
    print(f"\n诊断响应:")
    print(result['response'][:500])
else:
    print(f"❌ 错误：{result['response']}")

# 测试 4: 模型查询
print("\n\n【测试 4】模型查询")
print("-" * 70)
result = integration.process_message("有哪些模型？", "015566043909-1816211276", "Skytop")
print(f"✅ 类型：{result['type']}")
print(f"\n响应预览:")
print(result['response'][:300])

# 测试 5: 一般查询
print("\n\n【测试 5】一般查询")
print("-" * 70)
result = integration.process_message(
    "这个系统能做什么？",
    "015566043909-1816211276",
    "Skytop"
)
print(f"✅ 类型：{result['type']}")
print(f"\n响应预览:")
print(result['response'][:300])

print("\n" + "=" * 70)
print("测试完成！")
print("=" * 70)
