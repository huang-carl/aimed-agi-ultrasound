"""
Conductor Agent API v1
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

router = APIRouter()


class TaskDispatchRequest(BaseModel):
    organs: List[str]
    image_paths: List[str]
    patient_id: str
    patient_name: Optional[str] = None


class TaskDispatchResponse(BaseModel):
    task_id: str
    status: str
    created_at: datetime


@router.post("/dispatch", response_model=TaskDispatchResponse, tags=["v1-总指挥"])
async def dispatch_task(request: TaskDispatchRequest):
    """
    任务分发接口 v1
    
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
    
    return TaskDispatchResponse(
        task_id=task_id,
        status="processing",
        created_at=datetime.now()
    )


@router.get("/task/{task_id}", tags=["v1-总指挥"])
async def get_task_status(task_id: str):
    """查询任务状态 v1"""
    return {
        "task_id": task_id,
        "status": "completed",
        "progress": 100,
        "results": {}
    }
