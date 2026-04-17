"""
Report Agent 测试
"""

import pytest
from agents.report_agent import ReportAgent

@pytest.fixture
def report_agent():
    return ReportAgent()

def test_report_initialization(report_agent):
    """测试 ReportAgent 初始化"""
    assert report_agent.template_dir == "templates"
    assert report_agent.output_dir == "data/reports"
    assert len(report_agent.supported_languages) == 6
    assert report_agent.report_count == 0

def test_generate_report(report_agent):
    """测试报告生成"""
    patient_info = {
        "patient_id": "PAT001",
        "name": "张三",
        "gender": "男",
        "age": 45
    }
    
    diagnosis_results = [
        {
            "organ": "胃",
            "diagnosis": "慢性胃炎",
            "probability": 0.85,
            "suggestion": "建议结合临床症状"
        },
        {
            "organ": "胰腺",
            "diagnosis": "未见明显异常",
            "probability": 0.92,
            "suggestion": "建议定期体检"
        }
    ]
    
    doctor_info = {
        "doctor_id": "DR001",
        "name": "李医生"
    }
    
    result = report_agent.generate_report(
        patient_info=patient_info,
        diagnosis_results=diagnosis_results,
        doctor_info=doctor_info,
        language="zh"
    )
    
    assert result["report_id"] is not None
    assert result["status"] == "success"
    assert "pdf_path" in result
    assert "content" in result
    assert result["content"]["language"] == "zh"

def test_generate_report_multilingual(report_agent):
    """测试多语言报告生成"""
    patient_info = {"patient_id": "PAT001", "name": "Test", "gender": "M", "age": 30}
    diagnosis_results = [{"organ": "胃", "diagnosis": "Normal", "probability": 0.9, "suggestion": "OK"}]
    doctor_info = {"doctor_id": "DR001", "name": "Dr. Smith"}
    
    for lang in ["zh", "en", "fr", "ja", "ko", "ru"]:
        result = report_agent.generate_report(
            patient_info=patient_info,
            diagnosis_results=diagnosis_results,
            doctor_info=doctor_info,
            language=lang
        )
        assert result["content"]["language"] == lang

def test_get_disclaimer(report_agent):
    """测试获取免责声明"""
    zh_disclaimer = report_agent._get_disclaimer("zh")
    assert "AI" in zh_disclaimer or "医生" in zh_disclaimer
    
    en_disclaimer = report_agent._get_disclaimer("en")
    assert "AI" in en_disclaimer or "physician" in en_disclaimer

def test_get_statistics(report_agent):
    """测试获取统计信息"""
    stats = report_agent.get_statistics()
    
    assert "total_reports" in stats
    assert "supported_languages" in stats
    assert "template_dir" in stats
    assert "output_dir" in stats
    assert len(stats["supported_languages"]) == 6
