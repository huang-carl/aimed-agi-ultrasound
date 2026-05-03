"""
Pancreas Agent API v2 - V2.0 架构
通过 PancreasAgent + Orchestrator 处理胰腺诊断请求
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from agents.pancreas_agent import pancreas_agent
from agents.base_agent import AgentMessage

router = APIRouter()


class PancreasDiagnosisResponse(BaseModel):
    organ: str
    disease: str
    probability: float
    suggestion: str
    image_quality: str
    risk_level: str
    findings: Optional[list] = None
    timestamp: datetime
    agent_version: str = "2.0"


@router.post("/diagnose", response_model=PancreasDiagnosisResponse, tags=["v1-胰腺诊断"])
async def diagnose_pancreas(file: UploadFile = File(...)):
    """
    胰腺超声影像诊断接口 v2 (V2.0 架构)
    
    通过 PancreasAgent 处理诊断请求
    """
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/dicom"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型：{file.content_type}")
    
    image_data = await file.read()
    image_format = file.content_type.split("/")[-1].lower()
    
    message = AgentMessage(
        sender_id="api_router",
        receiver_id="pancreas",
        message_type="diagnose",
        payload={
            "image_data": image_data,
            "image_format": image_format,
            "filename": file.filename
        }
    )
    
    try:
        response = await pancreas_agent.process(message)
        
        if response.message_type == "error":
            raise HTTPException(status_code=500, detail=response.payload.get("error", "诊断失败"))
        
        result = response.payload
        return PancreasDiagnosisResponse(
            organ=result.get("organ", "胰腺"),
            disease=result.get("diagnosis", "待明确"),
            probability=result.get("probability", 0.0),
            suggestion=result.get("suggestion", ""),
            image_quality=result.get("image_quality", {}).get("level", "unknown"),
            risk_level=result.get("risk_level", "unknown"),
            findings=result.get("findings"),
            timestamp=datetime.fromisoformat(result.get("timestamp", datetime.now().isoformat())),
            agent_version="2.0"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"诊断服务异常：{str(e)}")


@router.get("/status", tags=["v1-胰腺诊断"])
async def pancreas_status():
    """获取 PancreasAgent 状态"""
    stats = pancreas_agent.get_statistics()
    return {
        "agent": "PancreasAgent",
        "architecture": "V2.0",
        "capabilities": pancreas_agent.get_capabilities(),
        "statistics": stats
    }
