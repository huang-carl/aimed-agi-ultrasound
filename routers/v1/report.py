"""
Report Agent API v2 - V2.0 架构
通过 ReportAgent + Orchestrator 处理报告生成请求
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

from agents.report_agent import report_agent
from agents.base_agent import AgentMessage

router = APIRouter()


class DiagnosisResult(BaseModel):
    organ: str
    disease: str
    probability: float
    suggestion: str


class ReportGenerateRequest(BaseModel):
    patient_id: str
    patient_name: str
    diagnosis_results: List[DiagnosisResult]
    doctor_id: str
    doctor_name: str
    language: Optional[str] = "zh"


class ReportGenerateResponse(BaseModel):
    report_id: str
    patient_id: str
    status: str
    content: Optional[str] = None
    pdf_url: Optional[str] = None
    created_at: datetime
    agent_version: str = "2.0"


@router.post("/generate", response_model=ReportGenerateResponse, tags=["v1-报告生成"])
async def generate_report(request: ReportGenerateRequest):
    """
    诊断报告生成接口 v2 (V2.0 架构)
    
    通过 ReportAgent 生成诊断报告
    支持 6 语言：zh/en/ja/ko/fr/ru
    """
    supported_languages = ["zh", "en", "ja", "ko", "fr", "ru"]
    if request.language not in supported_languages:
        raise HTTPException(status_code=400, detail=f"不支持的语言：{request.language}")
    
    report_id = f"RPT_{datetime.now().strftime('%Y%m%d%H%M%S')}_{request.patient_id}"
    
    # 通过 ReportAgent 处理
    message = AgentMessage(
        sender_id="api_router",
        receiver_id="report",
        message_type="generate_report",
        payload={
            "patient_info": {
                "patient_id": request.patient_id,
                "name": request.patient_name
            },
            "diagnosis_results": [r.dict() for r in request.diagnosis_results],
            "doctor_info": {
                "doctor_id": request.doctor_id,
                "name": request.doctor_name
            },
            "language": request.language
        }
    )
    
    try:
        response = await report_agent.process(message)
        
        if response.message_type == "error":
            raise HTTPException(status_code=500, detail=response.payload.get("error", "报告生成失败"))
        
        result = response.payload
        # Map agent response to API response
        content = result.get("content", {})
        return ReportGenerateResponse(
            report_id=result.get("report_id", report_id),
            patient_id=request.patient_id,
            status=result.get("status", "generated"),
            content=str(content) if content else None,
            pdf_url=result.get("pdf_path"),
            created_at=datetime.now(),
            agent_version="2.0"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告服务异常：{str(e)}")


@router.get("/status", tags=["v1-报告生成"])
async def report_status():
    """获取 ReportAgent 状态"""
    stats = report_agent.get_statistics()
    return {
        "agent": "ReportAgent",
        "architecture": "V2.0",
        "capabilities": report_agent.get_capabilities(),
        "statistics": stats
    }
