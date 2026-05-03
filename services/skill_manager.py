"""
AIMED Skills 管理器
加载、解析、应用 AIMED 专属技能
"""

import os
import glob
from typing import Dict, List, Optional, Any
from datetime import datetime


class SkillManager:
    """技能管理器 - 加载和应用 AIMED 技能"""
    
    def __init__(self, skills_dir: str = None):
        if skills_dir is None:
            # 默认路径
            workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            skills_dir = os.path.join(workspace, "skills", "aimed")
        
        self.skills_dir = skills_dir
        self.skills: Dict[str, Dict[str, Any]] = {}
        self._load_skills()
    
    def _load_skills(self):
        """加载所有技能文件"""
        if not os.path.exists(self.skills_dir):
            print(f"[SkillManager] 技能目录不存在：{self.skills_dir}")
            return
        
        skill_files = glob.glob(os.path.join(self.skills_dir, "*.md"))
        
        for filepath in skill_files:
            filename = os.path.basename(filepath)
            if filename == "README.md":
                continue
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                skill_name = filename.replace('.md', '')
                skill_info = self._parse_skill(skill_name, content)
                self.skills[skill_name] = skill_info
                print(f"[SkillManager] ✅ 加载技能：{skill_name}")
            except Exception as e:
                print(f"[SkillManager] ⚠️ 加载技能失败 {filename}: {e}")
        
        print(f"[SkillManager] 共加载 {len(self.skills)} 个技能")
    
    def _parse_skill(self, name: str, content: str) -> Dict[str, Any]:
        """解析技能文件"""
        lines = content.split('\n')
        
        # 提取描述
        description = ""
        in_description = False
        for line in lines:
            if line.startswith("## 描述"):
                in_description = True
                continue
            if in_description:
                if line.startswith("## "):
                    break
                description += line.strip() + " "
        
        # 提取触发条件
        triggers = []
        in_triggers = False
        for line in lines:
            if line.startswith("## 触发条件"):
                in_triggers = True
                continue
            if in_triggers:
                if line.startswith("## "):
                    break
                if line.startswith("- "):
                    triggers.append(line[2:].strip())
        
        return {
            "name": name,
            "description": description.strip(),
            "triggers": triggers,
            "content": content,
            "file": f"{name}.md",
            "loaded_at": datetime.now().isoformat()
        }
    
    def get_skill(self, name: str) -> Optional[Dict[str, Any]]:
        """获取指定技能"""
        return self.skills.get(name)
    
    def list_skills(self) -> List[Dict[str, str]]:
        """列出所有技能"""
        return [
            {
                "name": s["name"],
                "description": s["description"][:100] + "..." if len(s["description"]) > 100 else s["description"],
                "triggers": s["triggers"]
            }
            for s in self.skills.values()
        ]
    
    def match_skill(self, query: str) -> Optional[str]:
        """根据查询匹配最相关技能"""
        query_lower = query.lower()
        
        # 关键词映射
        keyword_map = {
            "diagnostic-report-standard": ["报告", "report", "诊断报告", "报告模板", "输出报告"],
            "doctor-patient-communication": ["沟通", "话术", "患者", "解释", "通俗", "专业"],
            "image-analysis-workflow": ["图像", "图像分析", "流程", "预处理", "特征提取"],
            "compliance-check": ["合规", "检查", "声明", "免责声明", "对外发布"],
        }
        
        best_match = None
        best_score = 0
        
        for skill_name, keywords in keyword_map.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > best_score:
                best_score = score
                best_match = skill_name
        
        return best_match if best_score > 0 else None
    
    def get_prompt_template(self, skill_name: str, context: Dict[str, Any] = None) -> str:
        """获取技能提示词模板"""
        skill = self.get_skill(skill_name)
        if not skill:
            return f"技能 {skill_name} 不存在"
        
        content = skill["content"]
        
        # 替换上下文变量
        if context:
            for key, value in context.items():
                placeholder = f"{{{key}}}"
                content = content.replace(placeholder, str(value))
        
        return content
    
    def reload(self):
        """重新加载所有技能"""
        self.skills.clear()
        self._load_skills()
        return len(self.skills)


# 全局单例
_skill_manager: Optional[SkillManager] = None

def get_skill_manager() -> SkillManager:
    """获取技能管理器单例"""
    global _skill_manager
    if _skill_manager is None:
        _skill_manager = SkillManager()
    return _skill_manager
