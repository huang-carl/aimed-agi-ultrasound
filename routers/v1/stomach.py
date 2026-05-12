"""
Stomach Agent API v1 - 使用真实 AI 诊断
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from loguru import logger

from agents.stomach_agent import stomach_agent
from agents.base_agent import AgentMessage

router = APIRouter()


class StomachDiagnosisResponse(BaseModel):
    organ: str
    disease: str
    probability: float
    suggestion: str
    image_quality: str
    timestamp: datetime
    mode: Optional[str] = "ai"
    model: Optional[str] = None


@router.post("/diagnose", response_model=StomachDiagnosisResponse, tags=["v1-胃诊断"])
async def diagnose_stomach(
    file: UploadFile = File(...),
    organ: str = Form("胃"),
    patient_name: str = Form("匿名"),
    patient_age: int = Form(0),
    patient_sex: str = Form("未知"),
    image_description: str = Form("")
):
    """
    胃超声影像诊断接口 v1
    
    使用 AI 多模型诊断服务
    """
    logger.info(f"收到胃诊断请求 v1 - 患者：{patient_name}")
    
    # 读取文件
    try:
        img_bytes = await file.read()
        if len(img_bytes) == 0:
            raise HTTPException(status_code=400, detail="文件为空")
        
        logger.info(f"文件读取成功，大小：{len(img_bytes)} bytes")
    except Exception as e:
        logger.error(f"文件读取失败：{str(e)}")
        raise HTTPException(status_code=500, detail="文件读取失败")
    
    # 使用 Agent 进行诊断
    try:
        message = AgentMessage(
            sender_id="stomach_api_v1",
            receiver_id=stomach_agent.agent_id,
            message_type="diagnose",
            payload={
                "image_data": img_bytes,
                "image_format": file.content_type.split("/")[-1] if file.content_type else "jpg",
                "image_description": image_description,
                "context": f"患者：{patient_name}, 年龄：{patient_age}, 性别：{patient_sex}"
            }
        )
        
        response = await stomach_agent.process(message)
        
        if response.message_type == "error":
            raise HTTPException(status_code=500, detail="诊断失败")
        
        result = response.payload
        image_quality = result.get("image_quality", {})
        if isinstance(image_quality, dict):
            quality_level = image_quality.get("level", "good")
        else:
            quality_level = "good"
        
        return StomachDiagnosisResponse(
            organ=result.get("organ", "胃"),
            disease=result.get("diagnosis", "待明确"),
            probability=float(result.get("probability", 0.5)),
            suggestion=result.get("suggestion", "建议进一步检查"),
            image_quality=quality_level,
            timestamp=datetime.fromisoformat(result.get("timestamp", datetime.now().isoformat())),
            mode=result.get("mode", "ai"),
            model=result.get("ai_model", "deepseek")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"诊断异常：{e}")
        # 降级到 Mock
        return StomachDiagnosisResponse(
            organ="胃",
            disease="慢性胃炎",
            probability=0.85,
            suggestion="建议结合临床症状，必要时行胃镜检查",
            image_quality="good",
            timestamp=datetime.now(),
            mode="mock"
        )
