"""
Conductor Agent API v2 - 基于 V2.0 架构
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import asyncio
import logging

logger = logging.getLogger('aimed.conductor_v2')

router = APIRouter()


class TaskDispatchRequest(BaseModel):
    organs: List[str]
    image_paths: List[str]
    patient_id: Optional[str] = None
    patient_name: Optional[str] = None


class TaskDispatchResponse(BaseModel):
    task_id: str
    status: str
    created_at: datetime
    message: str


@router.post("/dispatch", response_model=TaskDispatchResponse, tags=["v1-总指挥"])
async def dispatch_task(request: TaskDispatchRequest):
    """
    任务分发接口 v2 - 使用 V2.0 架构
    
    支持器官：stomach（胃）, pancreas（胰腺）
    """
    supported_organs = ["stomach", "pancreas"]
    
    # 验证器官
    invalid_organs = [org for org in request.organs if org not in supported_organs]
    if invalid_organs:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的器官类型：{invalid_organs}"
        )
    
    # 生成任务 ID
    task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    # 使用 ConductorAgent V2.0 分发任务
    from agents.conductor_agent import conductor_agent
    
    task = conductor_agent.dispatch_task(
        organs=request.organs,
        image_paths=request.image_paths,
        patient_id=request.patient_id
    )
    
    return TaskDispatchResponse(
        task_id=task["task_id"],
        status=task["status"],
        created_at=task["created_at"],
        message=f"任务已分发到 {len(request.organs)} 个器官 Agent"
    )


@router.get("/task/{task_id}", tags=["v1-总指挥"])
async def get_task_status(task_id: str):
    """查询任务状态 v2 - 使用 V2.0 架构"""
    from agents.conductor_agent import conductor_agent
    
    task = conductor_agent.get_task_status(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在：{task_id}")
    
    return task


@router.post("/task/{task_id}/complete", tags=["v1-总指挥"])
async def complete_task(task_id: str, results: Dict[str, Any] = {}):
    """标记任务完成 v2"""
    from agents.conductor_agent import conductor_agent
    
    conductor_agent.complete_task(task_id, results)
    return {"task_id": task_id, "status": "completed"}


@router.get("/stats", tags=["v1-总指挥"])
async def get_conductor_stats():
    """获取 Conductor 统计信息 v2"""
    from agents.conductor_agent import conductor_agent
    
    return conductor_agent.get_statistics()


@router.post("/test/dispatch-stomach", tags=["v1-总指挥"])
async def test_dispatch_stomach():
    """测试：直接调用 StomachAgent 的 process 方法"""
    from agents.stomach_agent import stomach_agent
    from agents.base_agent import AgentMessage
    
    message = AgentMessage(
        sender_id="api_test",
        receiver_id="stomach",
        message_type="status",
        payload={}
    )
    
    response = await stomach_agent.process(message)
    
    return {
        "test": "stomach_agent_v2",
        "status": response.payload if response else None
    }


@router.post("/test/dispatch-pancreas", tags=["v1-总指挥"])
async def test_dispatch_pancreas():
    """测试：直接调用 PancreasAgent 的 process 方法"""
    from agents.pancreas_agent import pancreas_agent
    from agents.base_agent import AgentMessage
    
    message = AgentMessage(
        sender_id="api_test",
        receiver_id="pancreas",
        message_type="status",
        payload={}
    )
    
    response = await pancreas_agent.process(message)
    
    return {
        "test": "pancreas_agent_v2",
        "status": response.payload if response else None
    }
