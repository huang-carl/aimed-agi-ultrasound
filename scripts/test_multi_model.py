"""
多模型路由服务测试脚本
测试所有配置的模型
"""

import os
import sys
from datetime import datetime

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

print("=" * 80)
print("多模型路由服务测试")
print("=" * 80)

# 导入路由服务
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.multi_model_service import router

# 获取状态
status = router.get_status()
print(f"\n路由模式：{status['routing_mode']}")
print(f"上下文阈值：{status['context_threshold']}")
print(f"可用模型：{', '.join(status['available_models'])}")
print()

for name, info in status['models'].items():
    print(f"  {name}: {info['model']} - {info['status']}")

# 测试 1：简单诊断
print("\n" + "=" * 80)
print("测试 1：简单诊断（胃）")
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
    print(result['diagnosis']['raw_text'][:500])
else:
    print(f"\n❌ 诊断失败：{result['error']}")

# 测试 2：胰腺诊断
print("\n" + "=" * 80)
print("测试 2：胰腺诊断")
print("=" * 80)

result = router.diagnose(
    organ="胰腺",
    image_description="胰头区可见低回声结节，大小约 2.5×2.0cm，边界不清，内部回声不均",
    context="患者，男，58 岁，上腹隐痛伴消瘦 2 个月，黄疸 1 周"
)

if result["success"]:
    print(f"\n✅ 诊断成功")
    print(f"模型：{result['mode']}")
    print(f"耗时：{result['elapsed_time']}s")
    print(f"Token：{result['usage']}")
    print(f"\n诊断结果：")
    print(result['diagnosis']['raw_text'][:500])
else:
    print(f"\n❌ 诊断失败：{result['error']}")

# 测试 3：长文本诊断
print("\n" + "=" * 80)
print("测试 3：长文本诊断（完整病历）")
print("=" * 80)

long_context = """
【患者基本信息】
姓名：张某某，性别：男，年龄：52 岁
【主诉】上腹部隐痛 6 个月，加重 1 周
【现病史】患者 6 个月前无明显诱因出现上腹部隐痛，呈间歇性发作，疼痛程度中等，与进食无明显关系。
伴有反酸、嗳气，无恶心呕吐，无黑便。曾在外院行胃镜检查，提示"慢性浅表性胃炎"。
近 1 周来症状加重，疼痛频率增加。
【既往史】高血压病史 5 年，最高血压 160/100mmHg，口服氨氯地平控制可。
【超声检查】胃窦部黏膜增厚，回声不均，可见点状低回声区，黏膜下层连续，蠕动正常。
【实验室检查】幽门螺杆菌：阳性（C14 呼气试验，DOB=8.5）
"""

result = router.diagnose(
    organ="胃",
    image_description="胃窦部黏膜增厚，回声不均，可见点状低回声区",
    context=long_context
)

if result["success"]:
    print(f"\n✅ 诊断成功")
    print(f"模型：{result['mode']}")
    print(f"耗时：{result['elapsed_time']}s")
    print(f"Token：{result['usage']}")
    print(f"\n诊断结果：")
    print(result['diagnosis']['raw_text'][:500])
else:
    print(f"\n❌ 诊断失败：{result['error']}")

print("\n" + "=" * 80)
print("测试完成！")
print("=" * 80)
