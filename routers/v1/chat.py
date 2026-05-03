"""
聊天 API v1 - 通用对话接口
用于企业微信机器人等外部渠道的 AI 对话
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.model_router import ModelRouter

router = APIRouter()

# 初始化模型路由
model_router = None
try:
    model_router = ModelRouter()
    print("✅ 聊天服务：模型路由已加载")
except Exception as e:
    print(f"聊天服务模型路由初始化失败：{e}")

# 系统提示词 - 定义 AI 角色
SYSTEM_PROMPT = """你是 AIMED 充盈视界的 AI 助手，一个专业的胃胰疾病超声造影 AI诊断平台。

关于 AIMED：
- 全称：AIMED 充盈视界 FillingVision
- 定位：上消化道（胃、胰、胆管）早筛服务生态
- 公司：阿尔麦德智慧医疗（湖州）有限公司
- 官网：https://www.aius.xin
- 愿景：将三甲医院增强造影能力下沉至基层/体检中心

核心产品：
- 口服超声造影剂（胰腺型/胃肠型/胆管型）
- AI 多智能体诊断平台
- 标准化充盈超声造影检查流程

核心公式：AIMED = 三剂 + 一法 + 一系统
- 三剂：胰腺型 + 胃肠型 + 胆管型 口服超声造影剂
- 一法：标准化充盈超声造影检查流程
- 一系统：AI 多智能体诊断平台

公司架构：
- 东亚医药（母公司）+ 国械恒发（合作单位/股东单位）→ 共同负责造影剂产品线
- 阿尔麦德智慧医疗（核心子公司）→ AI诊断系统研发
- 阿尔麦德上海（子公司）→ 医疗器械运营
- 和七汇企业（合伙企业）→ 企业管理/投资咨询

回答要求：
1. 专业、友好、简洁
2. 涉及医疗诊断时，提醒用户这是辅助工具，不能替代专业医生诊断
3. 如果问题超出你的知识范围，诚实回答
4. 用中文回答"""


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str  # 用户消息
    context: Optional[str] = ""  # 额外上下文
    model: Optional[str] = "default"  # 模型选择


class ChatResponse(BaseModel):
    """聊天响应"""
    success: bool
    reply: str  # AI 回复
    task_id: str
    model: Optional[str] = None
    timestamp: str
    raw_text: Optional[str] = None


def mock_chat(message: str) -> str:
    """Mock 聊天（降级用）"""
    msg = message.lower()
    if "你好" in msg or "hello" in msg:
        return "你好！我是 AIMED 充盈视界的 AI 助手，很高兴为你服务。请问有什么可以帮助你的？"
    elif "诊断" in msg or "检查" in msg:
        return "AIMED 提供胃胰超声造影 AI诊断服务。我们的口服超声造影剂 + AI诊断平台，可以将三甲医院的增强造影能力下沉至基层体检中心。单次筛查仅需 100-200 元，10 分钟出报告。"
    elif "造影剂" in msg:
        return "我们的口服超声造影剂系列包括：胰腺型、胃肠型、胆管型。全球首创，不良反应率 <2%，安全性显著优于传统造影剂。由国械恒发（合作单位/股东单位）与母公司东亚医药共同负责。"
    elif "公司" in msg or "介绍" in msg:
        return "AIMED 充盈视界由阿尔麦德智慧医疗（湖州）有限公司发起，构建了从造影剂研发生产到 AI诊断的完整产业生态。官网：https://www.aius.xin"
    else:
        return f"收到你的消息：「{message}」\n\n我是 AIMED 充盈视界的 AI 助手，可以回答关于我们的产品、服务、技术等方面的问题。请问有什么具体想了解的吗？"


@router.post("/chat", response_model=ChatResponse, tags=["v1-聊天服务"])
async def chat(request: ChatRequest):
    """
    AI 聊天接口
    
    用于企业微信机器人等外部渠道的通用对话
    """
    try:
        task_id = f"chat_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # 检查模型路由
        if model_router is None:
            reply = mock_chat(request.message)
            return ChatResponse(
                success=True,
                reply=reply,
                task_id=task_id,
                model='mock',
                timestamp=datetime.now().isoformat()
            )
        
        # 构建对话消息
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": request.message}
        ]
        
        if request.context:
            messages.insert(1, {"role": "system", "content": f"额外上下文：{request.context}"})
        
        # 调用模型路由
        result = model_router.chat(
            messages=messages,
            model=request.model if request.model != "default" else None,
            temperature=0.7
        )
        
        if result.get('success'):
            return ChatResponse(
                success=True,
                reply=result.get('reply', result.get('content', '暂无回复')),
                task_id=task_id,
                model=result.get('model'),
                timestamp=datetime.now().isoformat(),
                raw_text=result.get('raw_text')
            )
        else:
            # 模型调用失败，降级到 Mock
            print(f"聊天模型调用失败：{result.get('error')}，降级到 Mock")
            reply = mock_chat(request.message)
            return ChatResponse(
                success=True,
                reply=reply,
                task_id=task_id,
                model='mock',
                timestamp=datetime.now().isoformat()
            )
        
    except Exception as e:
        print(f"聊天异常：{str(e)}")
        return ChatResponse(
            success=False,
            reply=f"系统异常：{str(e)}，请稍后重试",
            task_id=f"chat_error_{uuid.uuid4().hex[:8]}",
            model=None,
            timestamp=datetime.now().isoformat()
        )
