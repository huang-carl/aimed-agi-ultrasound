#!/usr/bin/env python3
"""
生成聘书 V2 - 管建明担任 阿尔麦德智慧医疗&南京大学-超声造影人工智能诊断联合实验室 副主任、实际基地主任
"""
from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT_DIR = "/root/.openclaw/workspace/attachments"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "聘书_管建明_副主任_基地主任.png")

W, H = 1400, 1000

# 创建背景
img = Image.new('RGB', (W, H), '#FAF6F0')
draw = ImageDraw.Draw(img)

# 字体
CJK_BOLD = "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Bold.ttc"
CJK_REG = "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc"

def font(size, bold=False):
    path = CJK_BOLD if bold else CJK_REG
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

# 边框 - 双线
draw.rectangle([20, 20, W-20, H-20], outline='#8B0000', width=4)
draw.rectangle([30, 30, W-30, H-30], outline='#8B0000', width=1)

# 装饰角
for cx, cy in [(35, 35), (W-75, 35), (35, H-75), (W-75, H-75)]:
    draw.rectangle([cx, cy, cx+40, cy+40], outline='#C41E3A', width=2)

# 顶部装饰线
draw.line([(100, 80), (W-100, 80)], fill='#C41E3A', width=2)

# 标题
draw.text((W//2, 120), '聘 书', fill='#8B0000', font=font(64, bold=True))
draw.line([(W//2 - 80, 190), (W//2 + 80, 190)], fill='#C41E3A', width=2)

# 正文
draw.text((W//2, 270), '兹聘请', fill='#333333', font=font(28))
draw.text((W//2, 340), '管 建 明', fill='#8B0000', font=font(56, bold=True))
draw.text((W//2, 410), '担任', fill='#333333', font=font(28))

# 实验室名称
draw.text((W//2, 480), '阿尔麦德智慧医疗 & 南京大学', fill='#1a73e8', font=font(22, bold=True))
draw.text((W//2, 530), '超声造影人工智能诊断联合实验室', fill='#1a73e8', font=font(24, bold=True))

# 职位
draw.text((W//2, 610), '副 主 任', fill='#8B0000', font=font(40, bold=True))
draw.text((W//2, 680), '实际基地主任', fill='#8B0000', font=font(36, bold=True))

# 分隔线
draw.line([(200, 750), (W-200, 750)], fill='#CCCCCC', width=1)

# 颁发单位
draw.text((W//2, 790), '阿尔麦德智慧医疗（湖州）有限公司', fill='#555555', font=font(20))
draw.text((W//2, 830), 'AIMED Smart Healthcare (Huzhou) Co., Ltd.', fill='#888888', font=font(14))
draw.text((W//2, 860), '南京大学', fill='#888888', font=font(14))

# 日期
draw.text((W//2, 910), '颁发日期：二〇二六年四月', fill='#555555', font=font(20))

# 底部装饰线
draw.line([(100, H-80), (W-100, H-80)], fill='#C41E3A', width=2)
draw.text((W//2, H-50), 'www.aius.xin', fill='#AAAAAA', font=font(14))

# 模拟印章
seal_x, seal_y = W - 180, H - 160
for i in range(3):
    draw.ellipse([seal_x-55+i, seal_y-55+i, seal_x+55-i, seal_y+55-i], outline='#CC0000', width=1)
draw.text((seal_x-22, seal_y-14), 'AIMED', fill='#CC0000', font=font(14, bold=True))
draw.text((seal_x-25, seal_y+5), '联合实验室', fill='#CC0000', font=font(12))

# 保存
img.save(OUTPUT_FILE, 'PNG', quality=95)
print(f"✅ 聘书已生成: {OUTPUT_FILE}")
print(f"文件大小: {os.path.getsize(OUTPUT_FILE) / 1024:.0f} KB")
