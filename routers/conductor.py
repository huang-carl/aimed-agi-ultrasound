from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from loguru import logger

router = APIRouter()

class TaskRequest(BaseModel):
    organs: List[str]  # ["stomach", "pancreas"]
    image_paths: List[str]
    patient_id: Optional[str] = None

class TaskResponse(BaseModel):
    task_id: str
    status: str
    results: Optional[dict] = None
    created_at: datetime

# 内存任务存储（生产环境应使用数据库）
task_store = {}

@router.post("/dispatch", response_model=TaskResponse, summary="任务分发 - 调度胃/胰腺诊断")
async def dispatch_task(request: TaskRequest):
    """
    总指挥任务分发接口
    根据请求的器官列表，调度对应的诊断 Agent
    """
    task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    logger.info(f"收到任务分发请求：{task_id}, 器官：{request.organs}")
    
    # 验证器官类型
    valid_organs = ["stomach", "pancreas"]
    for organ in request.organs:
        if organ not in valid_organs:
            raise HTTPException(status_code=400, detail=f"不支持的器官类型：{organ}")
    
    # 创建任务记录
    task = {
        "task_id": task_id,
        "status": "processing",
        "organs": request.organs,
        "image_paths": request.image_paths,
        "patient_id": request.patient_id,
        "created_at": datetime.now(),
        "results": {}
    }
    task_store[task_id] = task
    
    # TODO: 异步调用各器官诊断 Agent
    # 目前返回任务 ID，实际诊断需轮询或 webhook 通知
    
    logger.info(f"任务创建成功：{task_id}")
    
    return TaskResponse(
        task_id=task_id,
        status="processing",
        created_at=task["created_at"]
    )

@router.get("/task/{task_id}", response_model=TaskResponse, summary="查询任务状态")
async def get_task_status(task_id: str):
    """
    查询任务执行状态
    """
    if task_id not in task_store:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = task_store[task_id]
    return TaskResponse(
        task_id=task["task_id"],
        status=task["status"],
        results=task.get("results"),
        created_at=task["created_at"]
    )

@router.get("/health", summary="Conductor 健康检查")
async def health_check():
    return {"status": "ok", "service": "Conductor", "active_tasks": len(task_store)}
