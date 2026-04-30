#!/usr/bin/env python3
"""
生成 PPT 所需的 AI 架构图和视觉素材（Pillow 实现）
"""
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import math

OUTPUT_DIR = "/root/.openclaw/workspace/attachments/ppt_assets"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 配色
COLORS = {
    'blue': '#1a73e8',
    'blue_dark': '#0d47a1',
    'blue_light': '#e3f2fd',
    'blue_border': '#1565c0',
    'blue_mid': '#42a5f5',
    'green': '#34a853',
    'green_dark': '#1b5e20',
    'green_light': '#e8f5e9',
    'green_border': '#2e7d32',
    'green_mid': '#66bb6a',
    'orange': '#ff6d00',
    'orange_dark': '#bf360c',
    'orange_light': '#fff3e0',
    'orange_border': '#e65100',
    'orange_mid': '#ff9800',
    'purple': '#9c27b0',
    'purple_dark': '#4a148c',
    'purple_light': '#f3e5f5',
    'purple_border': '#7b1fa2',
    'purple_mid': '#ba68c8',
    'red': '#f44336',
    'red_light': '#fbe9e7',
    'yellow': '#ffc107',
    'yellow_light': '#fff8e1',
    'teal': '#009688',
    'white': '#ffffff',
    'bg': '#f8f9fa',
    'text': '#202124',
    'gray': '#5f6368',
    'gray_light': '#e8eaed',
    'gray_mid': '#dadce0',
}

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def draw_rounded_rect(draw, xy, wh, radius=12, fill=None, outline=None, width=2):
    x0, y0 = xy
    w, h = wh
    x1, y1 = x0 + w, y0 + h
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=outline, width=width)

def draw_text_centered(draw, x, y, text, font, fill=COLORS['text']):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((x - tw//2, y - th//2), text, fill=fill, font=font)

def draw_multiline_centered(draw, x, y, lines, font, line_spacing=1.5, fill=COLORS['gray']):
    total_h = sum(draw.textbbox((0, 0), l, font=font)[3] - draw.textbbox((0, 0), l, font=font)[1] 
                   for l in lines)
    spacing = line_spacing * (draw.textbbox((0, 0), 'A', font=font)[3] - draw.textbbox((0, 0), 'A', font=font)[1])
    start_y = y - total_h // 2
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        cy = start_y + i * spacing + th // 2
        draw.text((x - tw//2, cy - th//2), line, fill=fill, font=font)

# 字体 - 使用 Noto Sans CJK（支持中文）
CJK_FONT_BOLD = "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Bold.ttc"
CJK_FONT_REG = "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc"

def load_cjk_font(size):
    try:
        return ImageFont.truetype(CJK_FONT_REG, size)
    except:
        return ImageFont.load_default()

def load_cjk_bold_font(size):
    try:
        return ImageFont.truetype(CJK_FONT_BOLD, size)
    except:
        return load_cjk_font(size)

font_title = load_cjk_bold_font(28)
font_subtitle = load_cjk_bold_font(20)
font_body = load_cjk_font(16)
font_small = load_cjk_font(13)
font_tiny = load_cjk_font(11)
font_icon = load_cjk_font(24)

# ============================================================
# 图1: AI 三阶段诊断流程图
# ============================================================
def generate_stage_diagram():
    W, H = 1600, 700
    img = Image.new('RGB', (W, H), COLORS['white'])
    draw = ImageDraw.Draw(img)
    
    # 标题
    draw.text((W//2, 25), 'AI 三阶段智能诊断流程', fill=COLORS['blue'], font=font_title)
    
    stages = [
        {
            'title': '阶段一', 'subtitle': '数据采集与预处理',
            'color': COLORS['blue_light'], 'border': COLORS['blue_border'], 'title_color': COLORS['blue_dark'],
            'items': [
                ('📷 图像采集', ['超声图像采集', '质量评估 · 去噪增强', '图像标准化处理']),
                ('📋 信息整合', ['年龄/病史/风险因素', '高危人群自动识别']),
            ],
            'x': 50,
        },
        {
            'title': '阶段二', 'subtitle': 'AI 智能分析',
            'color': COLORS['green_light'], 'border': COLORS['green_border'], 'title_color': COLORS['green_dark'],
            'items': [
                ('🔍 病灶检测', ['胰腺轮廓勾画', '可疑病灶区域标注']),
                ('📐 特征量化', ['大小/形态/胰管测量', '回声特征分析']),
                ('🧠 智能分级', ['Su-RADS 分级评估', '恶性风险预测']),
            ],
            'x': 550,
        },
        {
            'title': '阶段三', 'subtitle': '报告生成',
            'color': COLORS['orange_light'], 'border': COLORS['orange_border'], 'title_color': COLORS['orange_dark'],
            'items': [
                ('📄 结构化报告', ['自动填充诊断结论', '分级建议处理方案']),
                ('👨⚕️ 医生复核', ['AI 标注人工确认', '补充临床意见']),
                ('🔐 区块链存证', ['报告不可篡改', '全程可追溯']),
            ],
            'x': 1050,
        },
    ]
    
    for stage in stages:
        x = stage['x']
        # 大框
        draw_rounded_rect(draw, (x, 55), (450, 580), radius=16, fill=stage['color'], outline=stage['border'], width=3)
        
        # 标题
        draw_text_centered(draw, x + 225, 85, stage['title'], font_subtitle, stage['title_color'])
        draw_text_centered(draw, x + 225, 115, stage['subtitle'], font_body, stage['border'])
        
        # 子项
        item_h = 170
        for i, (item_title, item_lines) in enumerate(stage['items']):
            iy = 150 + i * item_h
            draw_rounded_rect(draw, (x+20, iy), (410, item_h-15), radius=10, fill=COLORS['white'], outline=stage['border'], width=1)
            draw_text_centered(draw, x + 225, iy + 25, item_title, font_body, stage['border'])
            lh = font_body.size
            for j, line in enumerate(item_lines):
                draw.text((x + 30, iy + 50 + j * (lh + 4)), line, fill=COLORS['gray'], font=font_small)
    
    # 箭头
    for arrow_x in [510, 1010]:
        draw.polygon([(arrow_x, 340), (arrow_x+25, 340), (arrow_x+25, 320), (arrow_x+45, 350), (arrow_x+25, 380), (arrow_x+25, 360), (arrow_x, 360)], fill=COLORS['blue'])
        draw.text((arrow_x+8, 310), '→', fill=COLORS['blue'], font=font_subtitle)
    
    # 底部
    draw.text((W//2, 665), 'AIMED 充盈视界 · 超声造影人工智能联合实验室', fill=COLORS['gray'], font=font_small)
    
    img.save(os.path.join(OUTPUT_DIR, 'ai_3stage_diagram.png'), 'PNG')
    print("✅ 图1: AI 三阶段诊断流程图")


# ============================================================
# 图2: AI 系统架构全景图
# ============================================================
def generate_architecture_diagram():
    W, H = 1600, 900
    img = Image.new('RGB', (W, H), COLORS['white'])
    draw = ImageDraw.Draw(img)
    
    # 标题
    draw.text((W//2, 15), 'AIMED 充盈视界 · AI 智能诊断系统架构', fill=COLORS['blue'], font=font_title)
    
    layers = [
        {
            'y': 55, 'h': 100, 'title': '🖥️  用户界面层',
            'color': COLORS['blue_light'], 'border': COLORS['blue_border'],
            'items': ['医生工作台', '患者咨询台', '管理者看板', '开发者 API'],
        },
        {
            'y': 180, 'h': 180, 'title': '🧠  AI 智能分析层',
            'color': COLORS['green_light'], 'border': COLORS['green_border'],
            'items': [
                ('图像预处理', '去噪增强/标准化/ROI'),
                ('病灶检测', '胰腺分割/病灶定位'),
                ('特征提取', '形态学/纹理/血流'),
                ('智能诊断', 'Su-RADS分级/评估'),
            ],
        },
        {
            'y': 385, 'h': 130, 'title': '📊  数据层',
            'color': COLORS['orange_light'], 'border': COLORS['orange_border'],
            'items': [
                ('🗄️ 病例数据库', '500+ 标注病例'),
                ('📚 知识库', '专家共识/Su-RADS'),
                ('🔑 API 密钥池', '阿里云百炼/NVIDIA'),
            ],
        },
        {
            'y': 540, 'h': 90, 'title': '🔐  区块链存证层',
            'color': COLORS['purple_light'], 'border': COLORS['purple_border'],
            'items': ['DID 身份认证', '报告哈希上链', '全程审计追溯'],
        },
    ]
    
    for layer in layers:
        y = layer['y']
        h = layer['h']
        # 大框
        draw_rounded_rect(draw, (50, y), (1500, h), radius=14, fill=layer['color'], outline=layer['border'], width=2)
        # 标题
        draw.text((80, y + 10), layer['title'], fill=layer['border'], font=font_subtitle)
        
        # 子项
        item_w = 1500 // len(layer['items'])
        for i, item in enumerate(layer['items']):
            ix = 50 + i * item_w + 15
            if isinstance(item, tuple):
                title, desc = item
                draw_rounded_rect(draw, (ix, y + 40), (item_w - 30, h - 50), radius=8, fill=COLORS['white'], outline=layer['border'], width=1)
                draw_text_centered(draw, ix + (item_w-30)//2, y + 55, title, font_body, layer['border'])
                draw_text_centered(draw, ix + (item_w-30)//2, y + 80, desc, font_small, COLORS['gray'])
            else:
                draw_rounded_rect(draw, (ix, y + 40), (item_w - 30, h - 50), radius=8, fill=COLORS['white'], outline=layer['border'], width=1)
                draw_text_centered(draw, ix + (item_w-30)//2, y + h//2, item, font_body, layer['border'])
        
        # 箭头
        if layer != layers[-1]:
            arrow_y = y + h
            draw.polygon([(800, arrow_y), (800, arrow_y+20), (790, arrow_y+20), (800, arrow_y+35), (810, arrow_y+20), (800, arrow_y+20)], fill=layer['border'])
    
    # 底部
    draw.text((W//2, 660), 'FISCO BCOS 多链架构  |  数据本地化部署  |  符合医疗数据安全要求', fill=COLORS['gray'], font=font_body)
    
    img.save(os.path.join(OUTPUT_DIR, 'ai_system_architecture.png'), 'PNG')
    print("✅ 图2: AI 系统架构全景图")


# ============================================================
# 图3: 充盈造影前后对比示意图
# ============================================================
def generate_contrast_comparison():
    W, H = 1600, 1100
    img = Image.new('RGB', (W, H), COLORS['white'])
    draw = ImageDraw.Draw(img)
    
    # 标题
    draw.text((W//2, 10), '口服超声充盈造影 · 胰腺疾病对比示意图', fill=COLORS['blue'], font=font_title)
    
    titles = [
        '常规超声（未充盈）',
        '口服造影剂充盈后',
        '充盈 + AI 标注',
        '正常胰腺',
        '胰腺囊肿',
        '胰腺实性占位',
    ]
    
    # 生成6个超声模拟图
    np.random.seed(42)
    for idx in range(6):
        col = idx % 3
        row = idx // 3
        ox = 80 + col * 520
        oy = 60 + row * 500
        
        # 生成模拟超声图像
        size = 200
        if idx == 0:  # 未充盈 - 气体干扰
            data = np.random.normal(50, 20, (size, size)).astype(np.float32)
            # 气体伪影
            for _ in range(20):
                cx, cy = np.random.randint(0, size), np.random.randint(0, size)
                r = np.random.randint(5, 20)
                y, x = np.ogrid[:size, :size]
                mask = (x-cx)**2 + (y-cy)**2 < r**2
                data[mask] += np.random.uniform(20, 50)
            # 胰腺区域（模糊）
            y, x = np.ogrid[:size, :size]
            pancreas = ((x-100)**2/300 + (y-90)**2/100) < 1
            data[pancreas] = data[pancreas] * 0.5 + 55
            data = np.clip(data, 0, 100)
            
        elif idx == 1:  # 充盈后
            data = np.random.normal(40, 12, (size, size)).astype(np.float32)
            y, x = np.ogrid[:size, :size]
            # 胃窗
            stomach = ((x-100)**2/500 + (y-140)**2/150) < 1
            data[stomach] = 5
            # 胰腺
            pancreas = ((x-100)**2/250 + (y-85)**2/80) < 1
            data[pancreas] = 65
            # 胰管
            duct = ((x-100)**2/220 + (y-85)**2/40) < 0.4
            data[duct] = 25
            data = np.clip(data, 0, 100)
            
        elif idx == 2:  # AI 标注
            data = np.random.normal(40, 12, (size, size)).astype(np.float32)
            y, x = np.ogrid[:size, :size]
            stomach = ((x-100)**2/500 + (y-140)**2/150) < 1
            data[stomach] = 5
            pancreas = ((x-100)**2/250 + (y-85)**2/80) < 1
            data[pancreas] = 65
            data = np.clip(data, 0, 100)
            
        elif idx == 3:  # 正常
            data = np.random.normal(40, 10, (size, size)).astype(np.float32)
            y, x = np.ogrid[:size, :size]
            pancreas = ((x-100)**2/220 + (y-85)**2/70) < 1
            data[pancreas] = 60
            duct = ((x-100)**2/200 + (y-85)**2/35) < 0.4
            data[duct] = 25
            data = np.clip(data, 0, 100)
            
        elif idx == 4:  # 囊肿
            data = np.random.normal(40, 10, (size, size)).astype(np.float32)
            y, x = np.ogrid[:size, :size]
            pancreas = ((x-100)**2/220 + (y-85)**2/70) < 1
            data[pancreas] = 60
            cyst = ((x-110)**2/50 + (y-80)**2/50) < 1
            data[cyst] = 8
            data = np.clip(data, 0, 100)
            
        elif idx == 5:  # 占位
            data = np.random.normal(40, 10, (size, size)).astype(np.float32)
            y, x = np.ogrid[:size, :size]
            pancreas = ((x-100)**2/220 + (y-85)**2/70) < 1
            data[pancreas] = 60
            tumor = ((x-105)**2/60 + (y-78)**2/60) < 1
            data[tumor] = 25
            data = np.clip(data, 0, 100)
        
        # 转换为图像
        img_data = (data * 2.55).astype(np.uint8)
        us_img = Image.fromarray(img_data, mode='L')
        us_img = us_img.resize((400, 400), Image.LANCZOS)
        img.paste(us_img, (ox, oy))
        
        # 标题
        draw.text((ox + 200, oy + 410), titles[idx], fill=COLORS['text'], font=font_body)
        
        # 特殊标注
        if idx == 0:
            draw_rounded_rect(draw, (ox + 80, oy + 350), (240, 40), radius=8, fill=COLORS['red_light'], outline=COLORS['red'], width=2)
            draw.text((ox + 200, oy + 358), '气体干扰 · 显示不清', fill=COLORS['red'], font=font_small)
        elif idx == 1:
            draw_rounded_rect(draw, (ox + 80, oy + 350), (240, 40), radius=8, fill='#e8f5e9', outline=COLORS['green'], width=2)
            draw.text((ox + 200, oy + 358), '胃窗清晰 · 结构可见', fill=COLORS['green'], font=font_small)
        elif idx == 2:
            # AI 标注框
            draw.rectangle([ox+50, oy+30, ox+350, oy+180], outline=COLORS['red'], width=3)
            draw.text((ox+55, oy+175), 'AI: 胰腺轮廓', fill=COLORS['red'], font=font_small)
            draw.text((ox+55, oy+25), 'Su-RADS 1', fill=COLORS['blue'], font=font_small)
            draw_rounded_rect(draw, (ox + 80, oy + 350), (240, 40), radius=8, fill=COLORS['blue_light'], outline=COLORS['blue'], width=2)
            draw.text((ox + 200, oy + 358), 'AI 自动标注 · 智能分级', fill=COLORS['blue'], font=font_small)
        elif idx == 4:
            # 囊肿标注
            draw.ellipse([ox+120, oy+55, ox+190, oy+125], outline=COLORS['orange'], width=3)
            draw.text((ox+155, oy+45), '囊肿', fill=COLORS['orange'], font=font_small)
            draw_rounded_rect(draw, (ox + 100, oy + 350), (200, 40), radius=8, fill=COLORS['yellow_light'], outline=COLORS['yellow'], width=2)
            draw.text((ox + 200, oy + 358), 'Su-RADS 2 · 低危险', fill=COLORS['orange'], font=font_small)
        elif idx == 5:
            # 占位标注
            draw.rectangle([ox+80, oy+45, ox+200, oy+145], outline=COLORS['red'], width=3)
            draw.text((ox+140, oy+35), '占位', fill=COLORS['red'], font=font_small)
            draw_rounded_rect(draw, (ox + 80, oy + 350), (240, 40), radius=8, fill=COLORS['red_light'], outline=COLORS['red'], width=2)
            draw.text((ox + 200, oy + 358), 'Su-RADS 4 · 高危险', fill=COLORS['red'], font=font_small)
    
    img.save(os.path.join(OUTPUT_DIR, 'contrast_comparison.png'), 'PNG')
    print("✅ 图3: 充盈造影前后对比示意图")


# ============================================================
# 图4: Su-RADS 分级标准图
# ============================================================
def generate_surads_chart():
    W, H = 1400, 800
    img = Image.new('RGB', (W, H), COLORS['white'])
    draw = ImageDraw.Draw(img)
    
    draw.text((W//2, 20), 'Su-RADS 胰腺超声造影分类标准', fill=COLORS['blue'], font=font_title)
    draw.text((W//2, 55), '参考 BI-RADS 体系 · AI 辅助分级', fill=COLORS['gray'], font=font_body)
    
    categories = [
        ('Su-RADS 1', '阴性', '胰腺形态正常，无异常发现', '常规体检', COLORS['green']),
        ('Su-RADS 2', '低危险度', '良性病变，恶性风险 <2%', '定期复查', COLORS['green']),
        ('Su-RADS 3', '中危险度', '可能良性，建议短期复查', '3-6月复查', COLORS['yellow']),
        ('Su-RADS 4', '高危险度', '可疑恶性，建议进一步检查', '增强CT/MRI', COLORS['orange']),
        ('Su-RADS 5', '极高危险度', '高度怀疑恶性，建议活检', '穿刺活检', COLORS['red']),
    ]
    
    bg_colors = ['#e8f5e9', '#e8f5e9', '#fff8e1', '#fff3e0', '#fbe9e7']
    
    for i, (grade, level, desc, action, color) in enumerate(categories):
        y = 100 + i * 130
        
        # 背景
        draw_rounded_rect(draw, (80, y), (1240, 110), radius=12, fill=bg_colors[i], outline=color, width=2)
        
        # 等级标签
        draw_rounded_rect(draw, (100, y+15), (180, 75), radius=10, fill=color, outline=None)
        draw_text_centered(draw, 190, y+35, grade, font_subtitle, COLORS['white'])
        draw_text_centered(draw, 190, y+60, level, font_small, COLORS['white'])
        
        # 描述
        draw.text((310, y+25), desc, fill=COLORS['gray'], font=font_body)
        
        # 建议
        draw_rounded_rect(draw, (900, y+20), (380, 65), radius=10, fill=COLORS['white'], outline=color, width=2)
        draw.text((920, y+35), f'→ {action}', fill=color, font=font_body)
    
    # 底部
    draw.text((W//2, 750), '💡 AI 辅助分级基于：形态学特征 + 回声特征 + 血流动力学 + 临床风险因素综合评估', fill=COLORS['gray'], font=font_small)
    
    img.save(os.path.join(OUTPUT_DIR, 'surads_chart.png'), 'PNG')
    print("✅ 图4: Su-RADS 分级标准图")


# ============================================================
# 图5: 核心优势对比图
# ============================================================
def generate_advantages_chart():
    W, H = 1400, 800
    img = Image.new('RGB', (W, H), COLORS['white'])
    draw = ImageDraw.Draw(img)
    
    draw.text((W//2, 20), 'AIMED 充盈视界 · 核心优势', fill=COLORS['blue'], font=font_title)
    
    advantages = [
        ('🎯', '精准', 'AI 辅助识别', '灵敏度 ≥85%\n特异度 ≥80%', '减少漏诊误诊', COLORS['blue']),
        ('💰', '经济', '成本优势', '仅为 CT/MRI 的 1/5', '适合大规模筛查', COLORS['green']),
        ('⚡', '高效', '快速分析', 'AI 分析 <3 分钟/例', '大幅提升效率', COLORS['red']),
        ('🔒', '安全', '无创无辐射', '可重复检查\n患者接受度高', '零辐射风险', COLORS['purple']),
        ('📊', '标准', '统一标准', 'Su-RADS 分级体系', '减少主观差异', COLORS['orange']),
        ('🌐', '普惠', '基层可用', '普通超声即可开展', '优质资源下沉', COLORS['teal']),
    ]
    
    for i, (icon, title, subtitle, desc, tag, color) in enumerate(advantages):
        col = i % 3
        row = i // 3
        x = 100 + col * 430
        y = 70 + row * 350
        
        # 卡片背景
        draw_rounded_rect(draw, (x, y), (400, 320), radius=16, fill=color, outline=color, width=2)
        # 半透明覆盖
        overlay = Image.new('RGBA', (400, 320), (*hex_to_rgb(color), 30))
        img_rgba = img.convert('RGBA')
        img_rgba.paste(overlay, (x, y), overlay.split()[3])
        img = img_rgba.convert('RGB')
        
        # 重新绘制边框
        draw_rounded_rect(draw, (x, y), (400, 320), radius=16, fill=None, outline=color, width=2)
        
        # 图标
        draw.text((x + 200, y + 30), icon, fill=color, font=font_icon)
        # 标题
        draw_text_centered(draw, x + 200, y + 75, title, font_subtitle, color)
        draw_text_centered(draw, x + 200, y + 105, subtitle, font_small, COLORS['gray'])
        # 描述
        lines = desc.split('\n')
        for j, line in enumerate(lines):
            draw.text((x + 200, y + 140 + j * 25), line, fill=COLORS['gray'], font=font_body)
        # 标签
        draw_rounded_rect(draw, (x + 100, y + 250), (200, 40), radius=8, fill=color, outline=None)
        alpha_overlay = Image.new('RGBA', (200, 40), (*hex_to_rgb(color), 40))
        img_rgba = img.convert('RGBA')
        img_rgba.paste(alpha_overlay, (x + 100, y + 250), alpha_overlay.split()[3])
        img = img_rgba.convert('RGB')
        draw.text((x + 200, y + 258), tag, fill=color, font=font_small)
    
    img.save(os.path.join(OUTPUT_DIR, 'advantages_chart.png'), 'PNG')
    print("✅ 图5: 核心优势对比图")


# ============================================================
# 图6: 发展路线图
# ============================================================
def generate_roadmap():
    W, H = 1600, 700
    img = Image.new('RGB', (W, H), COLORS['white'])
    draw = ImageDraw.Draw(img)
    
    draw.text((W//2, 15), 'AIMED 发展路线图', fill=COLORS['blue'], font=font_title)
    
    phases = [
        {
            'name': 'Phase 1', 'time': '2026 Q2-Q4', 'pos': '科研工具',
            'color': COLORS['green'], 'x': 300,
            'items': ['技术验证与优化', '积累 500+ 标注病例', 'AI 准确率 ≥85%', '科研合作模式', '伦理审查通过'],
        },
        {
            'name': 'Phase 2', 'time': '2027 Q1-Q3', 'pos': '产品化',
            'color': COLORS['blue'], 'x': 800,
            'items': ['二类器械备案', '试点医院验证', '标准化操作流程', '多中心临床研究', '医生培训体系'],
        },
        {
            'name': 'Phase 3', 'time': '2027 Q4+', 'pos': '规模化',
            'color': COLORS['purple'], 'x': 1300,
            'items': ['NMPA 三类证申报', '规模化临床应用', '医保覆盖探索', '基层医院推广', '多病种扩展'],
        },
    ]
    
    # 时间线
    draw.line([(100, 350), (1500, 350)], fill=COLORS['gray_light'], width=4)
    
    for phase in phases:
        x = phase['x']
        y = 350
        
        # 节点
        draw.ellipse([x-15, y-15, x+15, y+15], fill=phase['color'])
        draw.text((x, y-8), phase['name'][-1], fill=COLORS['white'], font=font_body)
        
        # 标题
        draw.text((x, y - 50), phase['name'], fill=phase['color'], font=font_subtitle)
        draw.text((x, y - 25), phase['time'], fill=COLORS['gray'], font=font_small)
        
        # 定位标签
        draw_rounded_rect(draw, (x-50, y+25), (100, 30), radius=6, fill=phase['color'], outline=None)
        draw.text((x, y+30), phase['pos'], fill=COLORS['white'], font=font_small)
        
        # 里程碑
        items_y = y + 70 if phase['name'] != 'Phase 2' else y + 70
        for j, item in enumerate(phase['items']):
            iy = y + 70 + j * 35
            draw.line([(x, y + 55), (x, iy - 5)], fill=phase['color'], width=1)
            draw_rounded_rect(draw, (x-120, iy - 12), (240, 28), radius=6, fill=COLORS['white'], outline=phase['color'], width=1)
            draw.text((x, iy - 5), f'✓ {item}', fill=COLORS['text'], font=font_small)
    
    # 箭头
    draw.polygon([(1500, 345), (1520, 345), (1520, 335), (1540, 350), (1520, 365), (1520, 355), (1500, 355)], fill=COLORS['gray'])
    draw.text((1510, 360), '→', fill=COLORS['gray'], font=font_small)
    
    img.save(os.path.join(OUTPUT_DIR, 'roadmap.png'), 'PNG')
    print("✅ 图6: 发展路线图")


# ============================================================
# 生成所有图表
# ============================================================
if __name__ == '__main__':
    generate_stage_diagram()
    generate_architecture_diagram()
    generate_contrast_comparison()
    generate_surads_chart()
    generate_advantages_chart()
    generate_roadmap()
    print(f"\n🎉 所有图表已生成到: {OUTPUT_DIR}")
    print("文件列表:")
    for f in sorted(os.listdir(OUTPUT_DIR)):
        size = os.path.getsize(os.path.join(OUTPUT_DIR, f))
        print(f"  {f} ({size/1024:.0f} KB)")
