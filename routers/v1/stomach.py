"""
Stomach Agent API v2 - V2.0 架构
通过 StomachAgent + Orchestrator 处理胃诊断请求
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import base64
import io

from agents.stomach_agent import stomach_agent
from agents.base_agent import AgentMessage

router = APIRouter()


class StomachDiagnosisResponse(BaseModel):
    organ: str
    disease: str
    probability: float
    suggestion: str
    image_quality: str
    risk_level: str
    findings: Optional[list] = None
    timestamp: datetime
    agent_version: str = "2.0"


@router.post("/diagnose", response_model=StomachDiagnosisResponse, tags=["v1-胃诊断"])
async def diagnose_stomach(file: UploadFile = File(...)):
    """
    胃超声影像诊断接口 v2 (V2.0 架构)
    
    通过 StomachAgent 处理诊断请求，支持：
    - 影像质量评估
    - 病灶识别
    - 诊断建议生成
    """
    # 验证文件类型
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/dicom"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型：{file.content_type}")
    
    # 读取图像数据
    image_data = await file.read()
    image_format = file.content_type.split("/")[-1].upper()
    if image_format == "JPG":
        image_format = "JPEG"
    
    # 通过 StomachAgent 处理
    message = AgentMessage(
        sender_id="api_router",
        receiver_id="stomach",
        message_type="diagnose",
        payload={
            "image_data": image_data,
            "image_format": image_format.lower(),
            "filename": file.filename
        }
    )
    
    try:
        response = await stomach_agent.process(message)
        
        if response.message_type == "error":
            raise HTTPException(status_code=500, detail=response.payload.get("error", "诊断失败"))
        
        result = response.payload
        return StomachDiagnosisResponse(
            organ=result.get("organ", "胃"),
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


@router.get("/status", tags=["v1-胃诊断"])
async def stomach_status():
    """获取 StomachAgent 状态"""
    stats = stomach_agent.get_statistics()
    return {
        "agent": "StomachAgent",
        "architecture": "V2.0",
        "capabilities": stomach_agent.get_capabilities(),
        "statistics": stats
    }
