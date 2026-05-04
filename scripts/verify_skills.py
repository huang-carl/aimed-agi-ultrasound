#!/usr/bin/env python3
"""
AIMED Hermes Skills 技能库测试脚本
验证技能文件是否完整、格式是否正确
"""

import os
import sys
from pathlib import Path

# 技能库目录
SKILLS_DIR = Path(__file__).parent.parent / "skills" / "aimed"

# 必需的技能文件
REQUIRED_SKILLS = [
    "diagnostic-report-standard.md",
    "doctor-patient-communication.md",
    "image-analysis-workflow.md",
    "compliance-check.md",
]

def check_skill_file(filename):
    """检查单个技能文件"""
    filepath = SKILLS_DIR / filename
    
    if not filepath.exists():
        return False, f"❌ 文件不存在：{filename}"
    
    content = filepath.read_text(encoding='utf-8')
    
    if len(content) < 100:
        return False, f"⚠️ 文件内容过少（{len(content)} 字符）：{filename}"
    
    # 检查必需字段
    required_sections = ["# Skill:", "## 描述", "## 触发条件"]
    missing = [s for s in required_sections if s not in content]
    
    if missing:
        return False, f"⚠️ 缺少必需字段 {missing}：{filename}"
    
    return True, f"✅ {filename} ({len(content)} 字符)"

def main():
    print("=" * 60)
    print("AIMED Hermes Skills 技能库测试")
    print("=" * 60)
    print(f"技能库目录：{SKILLS_DIR}")
    print()
    
    # 检查目录是否存在
    if not SKILLS_DIR.exists():
        print(f"❌ 技能库目录不存在：{SKILLS_DIR}")
        sys.exit(1)
    
    # 检查每个技能文件
    all_ok = True
    for skill in REQUIRED_SKILLS:
        ok, msg = check_skill_file(skill)
        print(msg)
        if not ok:
            all_ok = False
    
    print()
    
    # 检查 README
    readme_path = SKILLS_DIR / "README.md"
    if readme_path.exists():
        print(f"✅ README.md 存在")
    else:
        print(f"⚠️ README.md 不存在")
        all_ok = False
    
    # 检查总览 README
    root_readme = SKILLS_DIR.parent / "README.md"
    if root_readme.exists():
        print(f"✅ 技能库总览 README.md 存在")
    else:
        print(f"⚠️ 技能库总览 README.md 不存在")
    
    print()
    print("=" * 60)
    if all_ok:
        print("✅ 所有技能文件检查通过！")
    else:
        print("⚠️ 部分技能文件存在问题，请检查")
    print("=" * 60)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
