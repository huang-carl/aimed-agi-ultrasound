"""
Stomach Agent API v1
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()


class StomachDiagnosisResponse(BaseModel):
    organ: str
    disease: str
    probability: float
    suggestion: str
    image_quality: str
    timestamp: datetime


@router.post("/diagnose", response_model=StomachDiagnosisResponse, tags=["v1-胃诊断"])
async def diagnose_stomach(file: UploadFile = File(...)):
    """
    胃超声影像诊断接口 v1
    
    返回诊断结果、置信度、建议
    """
    # 验证文件类型
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/dicom"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型：{file.content_type}"
        )
    
    # TODO: 接入真实 AI 模型
    # 当前使用 mock 数据
    return StomachDiagnosisResponse(
        organ="胃",
        disease="慢性胃炎",
        probability=0.85,
        suggestion="建议结合临床症状，必要时行胃镜检查",
        image_quality="good",
        timestamp=datetime.now()
    )
