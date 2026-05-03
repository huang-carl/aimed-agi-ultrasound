#!/usr/bin/env python3
"""
Skill 沉淀自动化脚本
从反馈中提取可沉淀为 skill 的内容，生成 skill 更新建议
"""

import os
import json
import glob
from datetime import datetime
from typing import List, Dict, Any


class SkillCurationEngine:
    """Skill 沉淀引擎 - 从反馈中提炼 skill"""
    
    def __init__(self, workspace_dir: str = None):
        if workspace_dir is None:
            workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.workspace_dir = workspace_dir
        self.feedback_dir = os.path.join(workspace_dir, "data", "feedback")
        self.skills_dir = os.path.join(workspace_dir, "skills", "aimed")
        self.candidates_dir = os.path.join(self.feedback_dir, "skill_candidates")
    
    def collect_feedback(self, days: int = 7) -> List[Dict[str, Any]]:
        """收集最近 N 天的反馈"""
        if not os.path.exists(self.feedback_dir):
            return []
        
        feedback_files = glob.glob(os.path.join(self.feedback_dir, "fb_*.json"))
        recent_feedback = []
        
        for filepath in feedback_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    record = json.load(f)
                
                # 解析时间戳
                ts = record.get("timestamp", "")
                if ts:
                    try:
                        feedback_time = datetime.fromisoformat(ts)
                    except (ValueError, AttributeError):
                        # Python 3.6 兼容
                        feedback_time = datetime.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S")
                    
                    if (datetime.now() - feedback_time).days <= days:
                        recent_feedback.append(record)
            except Exception as e:
                print(f"⚠️ 解析反馈失败 {filepath}: {e}")
        
        return recent_feedback
    
    def analyze_feedback_patterns(self, feedback_list: List[Dict]) -> Dict[str, Any]:
        """分析反馈模式，识别可沉淀为 skill 的内容"""
        patterns = {
            "format_issues": [],      # 格式问题
            "accuracy_issues": [],    # 准确性问题
            "communication_issues": [], # 沟通问题
            "compliance_issues": [],  # 合规问题
            "suggestions": []         # 改进建议
        }
        
        for fb in feedback_list:
            fb_type = fb.get("feedback_type", "")
            comment = fb.get("comment", "")
            suggestion = fb.get("suggested_improvement", "")
            
            if "format" in fb_type:
                patterns["format_issues"].append({
                    "comment": comment,
                    "suggestion": suggestion,
                    "user_type": fb.get("user_type", ""),
                    "rating": fb.get("rating", 0)
                })
            elif "accuracy" in fb_type:
                patterns["accuracy_issues"].append({
                    "comment": comment,
                    "suggestion": suggestion,
                    "user_type": fb.get("user_type", ""),
                    "rating": fb.get("rating", 0)
                })
            elif "communication" in fb_type:
                patterns["communication_issues"].append({
                    "comment": comment,
                    "suggestion": suggestion,
                    "user_type": fb.get("user_type", ""),
                    "rating": fb.get("rating", 0)
                })
            
            if suggestion:
                patterns["suggestions"].append({
                    "suggestion": suggestion,
                    "feedback_type": fb_type,
                    "user_type": fb.get("user_type", ""),
                    "is_skill_trigger": fb.get("is_skill_trigger", False)
                })
        
        return patterns
    
    def generate_skill_update(self, patterns: Dict[str, Any]) -> List[Dict[str, str]]:
        """根据反馈模式生成 skill 更新建议"""
        updates = []
        
        # 格式问题 → 更新 diagnostic-report-standard
        if patterns["format_issues"]:
            updates.append({
                "skill": "diagnostic-report-standard",
                "action": "update",
                "reason": f"发现 {len(patterns['format_issues'])} 个格式问题反馈",
                "suggested_changes": self._extract_common_themes(patterns["format_issues"])
            })
        
        # 沟通问题 → 更新 doctor-patient-communication
        if patterns["communication_issues"]:
            updates.append({
                "skill": "doctor-patient-communication",
                "action": "update",
                "reason": f"发现 {len(patterns['communication_issues'])} 个沟通问题反馈",
                "suggested_changes": self._extract_common_themes(patterns["communication_issues"])
            })
        
        # 新 skill 候选
        skill_triggers = [s for s in patterns["suggestions"] if s.get("is_skill_trigger")]
        if skill_triggers:
            updates.append({
                "skill": "new_skill",
                "action": "create",
                "reason": f"收到 {len(skill_triggers)} 个 skill 创建建议",
                "suggested_changes": self._extract_common_themes(skill_triggers)
            })
        
        return updates
    
    def _extract_common_themes(self, items: List[Dict]) -> str:
        """提取共同主题"""
        if not items:
            return "无"
        
        # 简单提取：合并所有建议
        themes = []
        for item in items:
            text = item.get("suggestion", "") or item.get("comment", "")
            if text and len(text) > 5:
                themes.append(f"- {text}")
        
        return "\n".join(themes[:10])  # 最多取 10 条
    
    def run_curation(self, days: int = 7) -> Dict[str, Any]:
        """运行完整的沉淀流程"""
        print("=" * 60)
        print("Skill 沉淀引擎 - 自动分析反馈")
        print("=" * 60)
        
        # 1. 收集反馈
        print(f"\n📊 收集最近 {days} 天的反馈...")
        feedback_list = self.collect_feedback(days)
        print(f"   找到 {len(feedback_list)} 条反馈")
        
        if not feedback_list:
            return {"status": "no_feedback", "message": "暂无反馈数据"}
        
        # 2. 分析模式
        print("\n🔍 分析反馈模式...")
        patterns = self.analyze_feedback_patterns(feedback_list)
        
        print(f"   格式问题：{len(patterns['format_issues'])} 条")
        print(f"   准确性问题：{len(patterns['accuracy_issues'])} 条")
        print(f"   沟通问题：{len(patterns['communication_issues'])} 条")
        print(f"   改进建议：{len(patterns['suggestions'])} 条")
        
        # 3. 生成更新建议
        print("\n📝 生成 skill 更新建议...")
        updates = self.generate_skill_update(patterns)
        
        for update in updates:
            print(f"   [{update['action'].upper()}] {update['skill']}")
            print(f"      原因：{update['reason']}")
        
        # 4. 保存分析报告
        report = {
            "generated_at": datetime.now().isoformat(),
            "feedback_count": len(feedback_list),
            "patterns": {
                "format_issues": len(patterns["format_issues"]),
                "accuracy_issues": len(patterns["accuracy_issues"]),
                "communication_issues": len(patterns["communication_issues"]),
                "suggestions": len(patterns["suggestions"])
            },
            "updates": updates
        }
        
        report_dir = os.path.join(self.workspace_dir, "data", "curation_reports")
        os.makedirs(report_dir, exist_ok=True)
        
        report_file = os.path.join(report_dir, f"curation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 分析报告已保存：{report_file}")
        print("=" * 60)
        
        return report


def main():
    """主函数"""
    engine = SkillCurationEngine()
    result = engine.run_curation(days=7)
    
    if result.get("status") == "no_feedback":
        print("\n💡 提示：暂无反馈数据，请先通过 /api/v1/feedback 接口提交反馈")
        return 0
    
    updates = result.get("updates", [])
    if not updates:
        print("\n✅ 当前反馈无需 skill 更新")
        return 0
    
    print(f"\n📋 共生成 {len(updates)} 个 skill 更新建议")
    print("   请人工审核后决定是否应用")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
