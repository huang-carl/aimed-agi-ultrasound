"""
Conductor Agent 测试
"""

import pytest
from agents.conductor_agent import ConductorAgent

@pytest.fixture
def conductor():
    return ConductorAgent()

def test_conductor_initialization(conductor):
    """测试 Conductor 初始化"""
    assert conductor.agent_registry == {}
    assert conductor.task_queue == []
    assert conductor.completed_tasks == {}

def test_register_agent(conductor):
    """测试注册 Agent"""
    mock_agent = {"name": "mock"}
    conductor.register_agent("stomach", mock_agent)
    assert "stomach" in conductor.agent_registry
    assert conductor.agent_registry["stomach"] == mock_agent

def test_dispatch_task_valid(conductor):
    """测试任务分发（有效器官）"""
    # 先注册 Agent
    conductor.register_agent("stomach", {"name": "stomach_agent"})
    conductor.register_agent("pancreas", {"name": "pancreas_agent"})
    
    result = conductor.dispatch_task(
        organs=["stomach", "pancreas"],
        image_paths=["/path/to/image1.png", "/path/to/image2.png"],
        patient_id="PAT001"
    )
    
    assert result["task_id"] is not None
    assert result["status"] == "processing"
    assert "stomach" in result["results"]
    assert "pancreas" in result["results"]

def test_dispatch_task_invalid_organ(conductor):
    """测试任务分发（无效器官）"""
    result = conductor.dispatch_task(
        organs=["liver"],  # 不支持的器官
        image_paths=["/path/to/image.png"]
    )
    
    assert result["status"] == "failed"
    assert len(result["errors"]) > 0

def test_get_task_status(conductor):
    """测试查询任务状态"""
    conductor.register_agent("stomach", {})
    
    # 创建任务
    dispatch_result = conductor.dispatch_task(
        organs=["stomach"],
        image_paths=["/path/to/image.png"]
    )
    task_id = dispatch_result["task_id"]
    
    # 查询状态
    status = conductor.get_task_status(task_id)
    assert status is not None
    assert status["task_id"] == task_id

def test_complete_task(conductor):
    """测试完成任务"""
    conductor.register_agent("stomach", {})
    
    # 创建任务
    dispatch_result = conductor.dispatch_task(
        organs=["stomach"],
        image_paths=["/path/to/image.png"]
    )
    task_id = dispatch_result["task_id"]
    
    # 完成任务
    conductor.complete_task(task_id, {"stomach": {"result": "success"}})
    
    # 验证状态
    status = conductor.get_task_status(task_id)
    assert status["status"] == "completed"

def test_get_statistics(conductor):
    """测试获取统计信息"""
    conductor.register_agent("stomach", {})
    conductor.register_agent("pancreas", {})
    
    stats = conductor.get_statistics()
    assert "total_tasks" in stats
    assert "pending_tasks" in stats
    assert "completed_tasks" in stats
    assert "registered_agents" in stats
    assert len(stats["registered_agents"]) == 2
