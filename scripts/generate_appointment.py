#!/usr/bin/env python3
"""
生成聘书 - 管建明担任 AIMED 超声造影人工智能诊断联合实验室 副主任
"""
from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT_DIR = "/root/.openclaw/workspace/attachments"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "聘书_管建明_副主任.png")

W, H = 1200, 850

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
draw.rectangle([20, 20, W-20, H-20], outline='#8B0000', width=3)
draw.rectangle([30, 30, W-30, H-30], outline='#8B0000', width=1)

# 装饰角
for cx, cy in [(35, 35), (W-75, 35), (35, H-75), (W-75, H-75)]:
    draw.rectangle([cx, cy, cx+40, cy+40], outline='#C41E3A', width=2)

# 顶部装饰线
draw.line([(100, 70), (W-100, 70)], fill='#C41E3A', width=2)

# 标题
draw.text((W//2, 100), '聘 书', fill='#8B0000', font=font(56, bold=True))
draw.line([(W//2 - 70, 160), (W//2 + 70, 160)], fill='#C41E3A', width=2)

# 正文
draw.text((W//2, 220), '兹聘请', fill='#333333', font=font(24))
draw.text((W//2, 280), '管 建 明', fill='#8B0000', font=font(48, bold=True))
draw.text((W//2, 350), '担任', fill='#333333', font=font(24))

# 实验室名称
draw.text((W//2, 410), 'AIMED 超声造影人工智能诊断联合实验室', fill='#1a73e8', font=font(20, bold=True))

# 职位
draw.text((W//2, 470), '副 主 任', fill='#8B0000', font=font(36, bold=True))

# 分隔线
draw.line([(200, 520), (W-200, 520)], fill='#CCCCCC', width=1)

# 颁发单位
draw.text((W//2, 560), '阿尔麦德智慧医疗（湖州）有限公司', fill='#555555', font=font(18))
draw.text((W//2, 595), 'AIMED Smart Healthcare (Huzhou) Co., Ltd.', fill='#888888', font=font(13))

# 日期
draw.text((W//2, 650), '颁发日期：二〇二六年四月', fill='#555555', font=font(18))

# 底部装饰线
draw.line([(100, H-75), (W-100, H-75)], fill='#C41E3A', width=2)
draw.text((W//2, H-45), 'www.aius.xin', fill='#AAAAAA', font=font(12))

# 模拟印章
seal_x, seal_y = W - 150, H - 180
for i in range(3):
    draw.ellipse([seal_x-50+i, seal_y-50+i, seal_x+50-i, seal_y+50-i], outline='#CC0000', width=1)
draw.text((seal_x-18, seal_y-12), 'AIMED', fill='#CC0000', font=font(12, bold=True))
draw.text((seal_x-20, seal_y+5), '联合实验室', fill='#CC0000', font=font(10))

# 保存
img.save(OUTPUT_FILE, 'PNG', quality=95)
print(f"✅ 聘书已生成: {OUTPUT_FILE}")
print(f"文件大小: {os.path.getsize(OUTPUT_FILE) / 1024:.0f} KB")
