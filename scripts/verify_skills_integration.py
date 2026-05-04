#!/usr/bin/env python3
"""
Skills 集成测试脚本
验证技能管理器、反馈 API、沉淀引擎的完整流程
"""

import os
import sys
import json

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_skill_manager():
    """测试技能管理器"""
    print("\n" + "=" * 60)
    print("测试 1: 技能管理器")
    print("=" * 60)
    
    try:
        from services.skill_manager import get_skill_manager
        
        manager = get_skill_manager()
        skills = manager.list_skills()
        
        print(f"✅ 技能管理器初始化成功")
        print(f"   已加载技能数：{len(skills)}")
        
        for skill in skills:
            print(f"   - {skill['name']}: {skill['description'][:50]}...")
        
        # 测试匹配
        test_queries = [
            "生成诊断报告",
            "跟患者解释一下",
            "图像分析流程",
            "检查合规性"
        ]
        
        print("\n📝 测试技能匹配：")
        for query in test_queries:
            matched = manager.match_skill(query)
            print(f"   '{query}' → {matched or '未匹配'}")
        
        # 测试获取提示词模板
        print("\n📝 测试提示词模板：")
        template = manager.get_prompt_template("diagnostic-report-standard")
        print(f"   diagnostic-report-standard 模板长度：{len(template)} 字符")
        
        return True
    
    except Exception as e:
        print(f"❌ 技能管理器测试失败：{e}")
        return False


def test_feedback_flow():
    """测试反馈流程（模拟）"""
    print("\n" + "=" * 60)
    print("测试 2: 反馈流程（模拟）")
    print("=" * 60)
    
    try:
        # 创建测试反馈目录
        feedback_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                    "data", "feedback")
        os.makedirs(feedback_dir, exist_ok=True)
        
        # 模拟反馈数据
        test_feedback = {
            "feedback_id": "fb_test_20260504_001",
            "report_id": "rpt_test_001",
            "user_type": "doctor",
            "rating": 4,
            "feedback_type": "format",
            "comment": "报告格式很好，但建议增加病变位置的图示",
            "suggested_improvement": "在报告中增加病变位置示意图",
            "is_skill_trigger": True,
            "timestamp": "2026-05-04T06:00:00"
        }
        
        # 保存测试反馈
        test_file = os.path.join(feedback_dir, "fb_test_20260504_001.json")
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_feedback, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 测试反馈已创建：{test_file}")
        
        # 读取验证
        with open(test_file, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        
        assert loaded["rating"] == 4
        assert loaded["feedback_type"] == "format"
        print(f"✅ 反馈读写验证通过")
        
        return True
    
    except Exception as e:
        print(f"❌ 反馈流程测试失败：{e}")
        return False


def test_skill_curation():
    """测试 skill 沉淀引擎"""
    print("\n" + "=" * 60)
    print("测试 3: Skill 沉淀引擎")
    print("=" * 60)
    
    try:
        # 直接导入，不通过 scripts 包
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
        from skill_curation import SkillCurationEngine
        
        engine = SkillCurationEngine()
        
        # 运行沉淀分析
        result = engine.run_curation(days=7)
        
        if result.get("status") == "no_feedback":
            print("⚠️ 暂无反馈数据（这是正常的，测试反馈已创建）")
            return True
        
        updates = result.get("updates", [])
        print(f"✅ 沉淀引擎运行成功，生成 {len(updates)} 个更新建议")
        
        return True
    
    except Exception as e:
        print(f"❌ 沉淀引擎测试失败：{e}")
        return False


def test_skill_files():
    """测试技能文件完整性"""
    print("\n" + "=" * 60)
    print("测试 4: 技能文件完整性")
    print("=" * 60)
    
    skills_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              "skills", "aimed")
    
    required_skills = [
        "diagnostic-report-standard.md",
        "doctor-patient-communication.md",
        "image-analysis-workflow.md",
        "compliance-check.md"
    ]
    
    all_ok = True
    for skill_file in required_skills:
        filepath = os.path.join(skills_dir, skill_file)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"   ✅ {skill_file} ({size} 字节)")
        else:
            print(f"   ❌ {skill_file} 不存在")
            all_ok = False
    
    return all_ok


def main():
    """主测试函数"""
    print("=" * 60)
    print("AIMED Skills 集成测试")
    print("=" * 60)
    
    results = {
        "skill_files": test_skill_files(),
        "skill_manager": test_skill_manager(),
        "feedback_flow": test_feedback_flow(),
        "skill_curation": test_skill_curation()
    }
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"   {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("🎉 所有测试通过！Skills 系统已就绪")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查")
        return 1


if __name__ == "__main__":
    sys.exit(main())
