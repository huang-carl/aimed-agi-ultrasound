"""
用户反馈路由
收集诊断反馈，用于 skill 沉淀和模型优化
"""

import os
import json
from typing import Optional
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class FeedbackRequest(BaseModel):
    """反馈请求"""
    report_id: str
    user_type: str = "doctor"  # doctor / patient / admin
    rating: int  # 1-5 星
    feedback_type: str = "general"  # general / format / accuracy / communication
    comment: str = ""
    suggested_improvement: str = ""
    is_skill_trigger: bool = False  # 是否触发 skill 沉淀


class FeedbackResponse(BaseModel):
    """反馈响应"""
    success: bool
    feedback_id: str
    message: str


# 反馈存储目录
FEEDBACK_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "feedback")


def ensure_feedback_dir():
    """确保反馈目录存在"""
    os.makedirs(FEEDBACK_DIR, exist_ok=True)


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: Request, feedback: FeedbackRequest):
    """
    提交用户反馈
    
    - **report_id**: 报告 ID
    - **user_type**: 用户类型（doctor/patient/admin）
    - **rating**: 评分（1-5）
    - **feedback_type**: 反馈类型
    - **comment**: 评论内容
    - **suggested_improvement**: 改进建议
    - **is_skill_trigger**: 是否触发 skill 沉淀
    """
    try:
        ensure_feedback_dir()
        
        # 生成反馈 ID
        feedback_id = f"fb_{datetime.now().strftime('%Y%m%d%H%M%S')}_{feedback.report_id}"
        
        # 构建反馈记录
        feedback_record = {
            "feedback_id": feedback_id,
            "report_id": feedback.report_id,
            "user_type": feedback.user_type,
            "rating": feedback.rating,
            "feedback_type": feedback.feedback_type,
            "comment": feedback.comment,
            "suggested_improvement": feedback.suggested_improvement,
            "is_skill_trigger": feedback.is_skill_trigger,
            "timestamp": datetime.now().isoformat(),
            "ip": request.client.host if request.client else "unknown"
        }
        
        # 保存反馈文件
        feedback_file = os.path.join(FEEDBACK_DIR, f"{feedback_id}.json")
        with open(feedback_file, 'w', encoding='utf-8') as f:
            json.dump(feedback_record, f, ensure_ascii=False, indent=2)
        
        # 如果触发 skill 沉淀，记录到 skill 候选
        if feedback.is_skill_trigger and feedback.suggested_improvement:
            await _trigger_skill_candidation(feedback_record)
        
        return FeedbackResponse(
            success=True,
            feedback_id=feedback_id,
            message="反馈已记录，感谢您的宝贵意见！"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"反馈提交失败：{str(e)}")


async def _trigger_skill_candidation(feedback_record: dict):
    """触发 skill 候选沉淀"""
    try:
        skill_candidates_dir = os.path.join(FEEDBACK_DIR, "skill_candidates")
        os.makedirs(skill_candidates_dir, exist_ok=True)
        
        candidate = {
            "source_feedback": feedback_record["feedback_id"],
            "suggestion": feedback_record["suggested_improvement"],
            "feedback_type": feedback_record["feedback_type"],
            "user_type": feedback_record["user_type"],
            "status": "pending_review",  # pending_review / approved / rejected
            "timestamp": datetime.now().isoformat()
        }
        
        candidate_file = os.path.join(skill_candidates_dir, f"{feedback_record['feedback_id']}_candidate.json")
        with open(candidate_file, 'w', encoding='utf-8') as f:
            json.dump(candidate, f, ensure_ascii=False, indent=2)
        
        print(f"[Feedback] 📝 新 skill 候选已记录：{feedback_record['feedback_id']}")
    
    except Exception as e:
        print(f"[Feedback] ⚠️ skill 候选记录失败：{e}")


@router.get("/feedback/stats")
async def get_feedback_stats():
    """获取反馈统计"""
    try:
        ensure_feedback_dir()
        
        feedback_files = [f for f in os.listdir(FEEDBACK_DIR) if f.endswith('.json')]
        
        if not feedback_files:
            return {
                "total": 0,
                "average_rating": 0,
                "by_type": {},
                "by_user_type": {}
            }
        
        total_ratings = []
        by_type = {}
        by_user_type = {}
        
        for filename in feedback_files:
            filepath = os.path.join(FEEDBACK_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                record = json.load(f)
            
            total_ratings.append(record.get("rating", 0))
            
            ft = record.get("feedback_type", "unknown")
            by_type[ft] = by_type.get(ft, 0) + 1
            
            ut = record.get("user_type", "unknown")
            by_user_type[ut] = by_user_type.get(ut, 0) + 1
        
        return {
            "total": len(feedback_files),
            "average_rating": round(sum(total_ratings) / len(total_ratings), 2) if total_ratings else 0,
            "by_type": by_type,
            "by_user_type": by_user_type
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"统计获取失败：{str(e)}")


@router.get("/feedback/skill_candidates")
async def get_skill_candidates():
    """获取 skill 候选列表"""
    try:
        skill_candidates_dir = os.path.join(FEEDBACK_DIR, "skill_candidates")
        if not os.path.exists(skill_candidates_dir):
            return {"candidates": []}
        
        candidates = []
        for filename in os.listdir(skill_candidates_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(skill_candidates_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    candidates.append(json.load(f))
        
        return {"candidates": candidates}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"候选列表获取失败：{str(e)}")
