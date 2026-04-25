"""
智谱 AI API 测试脚本
测试 GLM-4-Flash 模型连接和诊断能力
"""

import os
import sys
import json
from datetime import datetime

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 智谱 AI API 配置
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")
ZHIPU_MODEL = os.getenv("ZHIPU_MODEL", "glm-4-flash")
ZHIPU_BASE_URL = "https://open.bigmodel.cn/api/paas/v4/"

print("=" * 80)
print("智谱 AI API 测试")
print("=" * 80)

# 检查 API Key
if not ZHIPU_API_KEY:
    print("❌ ZHIPU_API_KEY 未配置")
    sys.exit(1)

print(f"\n✅ API Key 已配置：{ZHIPU_API_KEY[:10]}...{ZHIPU_API_KEY[-5:]}")
print(f"✅ 模型：{ZHIPU_MODEL}")
print(f"✅ Base URL：{ZHIPU_BASE_URL}")

# 测试 1：简单对话
print("\n" + "=" * 80)
print("测试 1：简单对话")
print("=" * 80)

try:
    from openai import OpenAI
    
    client = OpenAI(
        api_key=ZHIPU_API_KEY,
        base_url=ZHIPU_BASE_URL,
    )
    
    response = client.chat.completions.create(
        model=ZHIPU_MODEL,
        messages=[
            {"role": "system", "content": "你是一个医疗 AI 助手，擅长超声影像诊断。"},
            {"role": "user", "content": "你好，请介绍一下你自己。"}
        ],
        max_tokens=500,
        temperature=0.7
    )
    
    print(f"\n✅ 响应状态：{response.choices[0].finish_reason}")
    print(f"✅ 模型：{response.model}")
    print(f"✅ Token 使用：prompt={response.usage.prompt_tokens}, completion={response.usage.completion_tokens}")
    print(f"\n📝 回复内容：")
    print(response.choices[0].message.content)
    
except Exception as e:
    print(f"\n❌ 测试失败：{str(e)}")
    sys.exit(1)

# 测试 2：医疗诊断场景
print("\n" + "=" * 80)
print("测试 2：医疗诊断场景")
print("=" * 80)

try:
    system_prompt = """你是一名经验丰富的放射科医生，擅长超声影像诊断。
请根据提供的影像描述和病历信息，给出专业的诊断意见。
输出格式要求：
1. 诊断结论
2. 置信度（0-1 之间）
3. 鉴别诊断
4. 进一步检查建议
5. 治疗建议

请用中文回答。"""
    
    user_prompt = """
【检查部位】胃
【影像描述】胃窦部黏膜充血水肿，可见点状糜烂，蠕动正常
【病历信息】患者，男，45 岁，上腹隐痛 3 个月，反酸嗳气
"""
    
    response = client.chat.completions.create(
        model=ZHIPU_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=1000,
        temperature=0.7
    )
    
    print(f"\n✅ 响应状态：{response.choices[0].finish_reason}")
    print(f"✅ 模型：{response.model}")
    print(f"✅ Token 使用：prompt={response.usage.prompt_tokens}, completion={response.usage.completion_tokens}")
    print(f"\n📝 诊断结果：")
    print(response.choices[0].message.content)
    
except Exception as e:
    print(f"\n❌ 诊断测试失败：{str(e)}")

# 测试 3：长文本场景
print("\n" + "=" * 80)
print("测试 3：长文本场景（完整病历）")
print("=" * 80)

try:
    long_prompt = """
【患者基本信息】
姓名：张某某
性别：男
年龄：52 岁
职业：教师
就诊日期：2026-04-25

【主诉】
上腹部隐痛 6 个月，加重 1 周

【现病史】
患者 6 个月前无明显诱因出现上腹部隐痛，呈间歇性发作，疼痛程度中等，与进食无明显关系，无放射痛。
伴有反酸、嗳气，无恶心呕吐，无黑便。
曾在外院行胃镜检查，提示"慢性浅表性胃炎"，给予奥美拉唑治疗，症状有所缓解。
近 1 周来症状加重，疼痛频率增加，为求进一步诊治来我院。

【既往史】
高血压病史 5 年，最高血压 160/100mmHg，口服氨氯地平控制可。
否认糖尿病、冠心病史。
否认肝炎、结核等传染病史。
否认手术外伤史。
否认药物食物过敏史。

【家族史】
父亲患有高血压，母亲体健。
否认家族遗传病史。

【体格检查】
T: 36.5℃, P: 78 次/分，R: 18 次/分，BP: 135/85mmHg
神志清楚，查体合作。
全身皮肤黏膜无黄染，浅表淋巴结未触及肿大。
心肺听诊未见异常。
腹平软，上腹部轻压痛，无反跳痛及肌紧张。
肝脾肋下未触及，Murphy 征阴性。
移动性浊音阴性，肠鸣音正常。

【超声检查】
检查部位：胃
检查所见：胃窦部黏膜增厚，回声不均，可见点状低回声区，黏膜下层连续，蠕动正常。
超声提示：胃窦部黏膜病变，建议进一步检查。

【实验室检查】
血常规：WBC 6.5×10^9/L, Hb 135g/L, PLT 220×10^9/L
肝功能：ALT 25U/L, AST 22U/L, TBIL 12μmol/L
肾功能：BUN 5.2mmol/L, Cr 78μmol/L
幽门螺杆菌：阳性（C14 呼气试验，DOB=8.5）

【初步诊断】
1. 慢性胃炎急性发作
2. 幽门螺杆菌感染
3. 高血压病 2 级（中危）

【鉴别诊断】
1. 胃溃疡：患者有上腹痛，但疼痛无节律性，需胃镜鉴别
2. 胃癌：年龄>50 岁，需警惕，胃镜 + 活检确诊
3. 胰腺疾病：上腹痛需排除胰腺炎、胰腺肿瘤，查淀粉酶、腹部 CT

【诊疗计划】
1. 完善胃镜检查 + 活检
2. 幽门螺杆菌根除治疗（四联疗法）
3. 继续降压治疗
4. 定期随访
"""
    
    response = client.chat.completions.create(
        model=ZHIPU_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": long_prompt}
        ],
        max_tokens=1500,
        temperature=0.7
    )
    
    print(f"\n✅ 响应状态：{response.choices[0].finish_reason}")
    print(f"✅ 模型：{response.model}")
    print(f"✅ Token 使用：prompt={response.usage.prompt_tokens}, completion={response.usage.completion_tokens}")
    print(f"\n📝 诊断结果：")
    print(response.choices[0].message.content[:500] + "...")
    
except Exception as e:
    print(f"\n❌ 长文本测试失败：{str(e)}")

print("\n" + "=" * 80)
print("测试完成！")
print("=" * 80)
