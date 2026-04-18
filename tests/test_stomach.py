"""
Stomach Agent 测试
"""

import pytest
from agents.stomach_agent import StomachAgent

@pytest.fixture
def stomach_agent():
    return StomachAgent()

def test_stomach_initialization(stomach_agent):
    """测试 StomachAgent 初始化"""
    assert stomach_agent.model_path is None
    assert stomach_agent.diagnosis_count == 0

def test_load_model(stomach_agent):
    """测试加载模型"""
    model_path = "models/stomach_v1.pt"
    stomach_agent.load_model(model_path)
    assert stomach_agent.model_path == model_path

def test_diagnose(stomach_agent):
    """测试诊断功能"""
    # Mock 图像数据
    mock_image = b"fake_image_data"
    
    result = stomach_agent.diagnose(mock_image)
    
    assert result["organ"] == "胃"
    assert "timestamp" in result
    assert "image_quality" in result
    assert "findings" in result
    assert "diagnosis" in result
    assert "probability" in result
    assert "suggestion" in result
    assert result["probability"] > 0
    assert result["probability"] <= 1

def test_diagnose_increment_count(stomach_agent):
    """测试诊断计数递增"""
    mock_image = b"fake_image_data"
    
    initial_count = stomach_agent.diagnosis_count
    stomach_agent.diagnose(mock_image)
    assert stomach_agent.diagnosis_count == initial_count + 1
    
    stomach_agent.diagnose(mock_image)
    assert stomach_agent.diagnosis_count == initial_count + 2

def test_quality_check(stomach_agent):
    """测试质量评估"""
    mock_image = b"fake_image_data"
    
    result = stomach_agent.quality_check(mock_image)
    
    assert "passed" in result
    assert "score" in result
    assert "dimensions" in result
    assert result["score"] >= 0
    assert result["score"] <= 1

def test_get_statistics(stomach_agent):
    """测试获取统计信息"""
    stats = stomach_agent.get_statistics()
    
    assert "total_diagnoses" in stats
    assert "model_loaded" in stats
    assert "agent_type" in stats
    assert stats["agent_type"] == "stomach"
