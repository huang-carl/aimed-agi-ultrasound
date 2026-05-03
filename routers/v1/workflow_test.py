"""
工作流测试路由 - 验证 Orchestrator 工作流执行
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
import asyncio
import logging

logger = logging.getLogger('aimed.workflow_test')

router = APIRouter()


@router.get("/workflows")
async def list_workflows():
    """列出所有工作流"""
    from main import orchestrator
    
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator 未初始化")
    
    workflows = orchestrator.list_workflows()
    return {
        "total": len(workflows),
        "workflows": workflows
    }


@router.post("/workflow/execute/{workflow_name}")
async def execute_workflow_by_name(workflow_name: str, input_data: Optional[Dict[str, Any]] = None):
    """按名称执行工作流"""
    from main import orchestrator
    
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator 未初始化")
    
    # 查找工作流 ID
    workflow_id = None
    for wf in orchestrator.list_workflows():
        if wf['name'] == workflow_name or wf['workflow_id'] == workflow_name:
            workflow_id = wf['workflow_id']
            break
    
    if not workflow_id:
        available = [wf['name'] for wf in orchestrator.list_workflows()]
        raise HTTPException(
            status_code=404,
            detail=f"工作流不存在: {workflow_name}. 可用: {available}"
        )
    
    # 执行工作流
    initial_data = input_data or {}
    try:
        result = await orchestrator.execute_workflow(workflow_id, initial_data)
        return result
    except Exception as e:
        logger.error(f"工作流执行失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent/execute/{agent_id}")
async def execute_single_agent(agent_id: str, input_data: Optional[Dict[str, Any]] = None):
    """执行单个 Agent"""
    from main import orchestrator
    
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator 未初始化")
    
    try:
        result = await orchestrator.execute_agent(agent_id, input_data or {})
        return result
    except Exception as e:
        logger.error(f"Agent 执行失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orchestrator/stats")
async def get_orchestrator_stats():
    """获取编排器统计信息"""
    from main import orchestrator
    
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator 未初始化")
    
    return orchestrator.get_statistics()


@router.post("/test/stomach-diagnose")
async def test_stomach_diagnose():
    """测试：胃部诊断工作流"""
    from main import orchestrator
    
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator 未初始化")
    
    # 直接调用 stomach_agent 的 process 方法
    from agents.stomach_agent import stomach_agent
    from agents.base_agent import AgentMessage
    
    message = AgentMessage(
        sender_id="test",
        receiver_id="stomach",
        message_type="status",
        payload={}
    )
    
    response = await stomach_agent.process(message)
    
    return {
        "test": "stomach_agent_status",
        "response": response.payload if response else None
    }


@router.post("/test/conductor-dispatch")
async def test_conductor_dispatch():
    """测试：Conductor 任务分发"""
    from main import orchestrator
    
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator 未初始化")
    
    from agents.conductor_agent import conductor_agent
    from agents.base_agent import AgentMessage
    
    message = AgentMessage(
        sender_id="test",
        receiver_id="conductor",
        message_type="status",
        payload={}
    )
    
    response = await conductor_agent.process(message)
    
    return {
        "test": "conductor_status",
        "response": response.payload if response else None
    }
