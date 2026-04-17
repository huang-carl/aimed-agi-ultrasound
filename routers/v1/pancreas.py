"""
Pancreas Agent API v1
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class PancreasDiagnosisResponse(BaseModel):
    organ: str
    disease: str
    probability: float
    suggestion: str
    image_quality: str
    timestamp: datetime


@router.post("/diagnose", response_model=PancreasDiagnosisResponse, tags=["v1-胰腺诊断"])
async def diagnose_pancreas(file: UploadFile = File(...)):
    """
    胰腺超声影像诊断接口 v1
    
    返回诊断结果、置信度、建议
    """
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/dicom"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型：{file.content_type}"
        )
    
    # TODO: 接入真实 AI 模型
    return PancreasDiagnosisResponse(
        organ="胰腺",
        disease="胰腺回声均匀",
        probability=0.92,
        suggestion="未见明显异常，建议定期体检",
        image_quality="good",
        timestamp=datetime.now()
    )
