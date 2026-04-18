"""
Pancreas Agent 测试
"""

import pytest
from agents.pancreas_agent import PancreasAgent

@pytest.fixture
def pancreas_agent():
    return PancreasAgent()

def test_pancreas_initialization(pancreas_agent):
    """测试 PancreasAgent 初始化"""
    assert pancreas_agent.model_path is None
    assert pancreas_agent.diagnosis_count == 0

def test_load_model(pancreas_agent):
    """测试加载模型"""
    model_path = "models/pancreas_v1.pt"
    pancreas_agent.load_model(model_path)
    assert pancreas_agent.model_path == model_path

def test_diagnose(pancreas_agent):
    """测试诊断功能"""
    # Mock 图像数据
    mock_image = b"fake_image_data"
    
    result = pancreas_agent.diagnose(mock_image)
    
    assert result["organ"] == "胰腺"
    assert "timestamp" in result
    assert "image_quality" in result
    assert "findings" in result
    assert "diagnosis" in result
    assert "probability" in result
    assert "suggestion" in result
    assert result["probability"] > 0
    assert result["probability"] <= 1

def test_diagnose_increment_count(pancreas_agent):
    """测试诊断计数递增"""
    mock_image = b"fake_image_data"
    
    initial_count = pancreas_agent.diagnosis_count
    pancreas_agent.diagnose(mock_image)
    assert pancreas_agent.diagnosis_count == initial_count + 1
    
    pancreas_agent.diagnose(mock_image)
    assert pancreas_agent.diagnosis_count == initial_count + 2

def test_quality_check(pancreas_agent):
    """测试质量评估"""
    mock_image = b"fake_image_data"
    
    result = pancreas_agent.quality_check(mock_image)
    
    assert "passed" in result
    assert "score" in result
    assert "dimensions" in result
    assert result["score"] >= 0
    assert result["score"] <= 1

def test_segment_organ(pancreas_agent):
    """测试器官分割"""
    mock_image = b"fake_image_data"
    
    result = pancreas_agent.segment_organ(mock_image)
    
    assert "segmented" in result
    assert "bounding_box" in result
    assert "confidence" in result

def test_get_statistics(pancreas_agent):
    """测试获取统计信息"""
    stats = pancreas_agent.get_statistics()
    
    assert "total_diagnoses" in stats
    assert "model_loaded" in stats
    assert "agent_type" in stats
    assert stats["agent_type"] == "pancreas"
