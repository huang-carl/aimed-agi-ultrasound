"""
Report Agent API v1
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

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
    pdf_url: Optional[str]
    created_at: datetime


@router.post("/generate", response_model=ReportGenerateResponse, tags=["v1-报告生成"])
async def generate_report(request: ReportGenerateRequest):
    """
    诊断报告生成接口 v1
    
    支持 6 语言：zh/en/ja/ko/fr/ru
    """
    supported_languages = ["zh", "en", "ja", "ko", "fr", "ru"]
    if request.language not in supported_languages:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的语言：{request.language}"
        )
    
    # 生成报告 ID
    report_id = f"RPT_{datetime.now().strftime('%Y%m%d%H%M%S')}_{request.patient_id}"
    
    # TODO: 生成真实 PDF 报告
    return ReportGenerateResponse(
        report_id=report_id,
        patient_id=request.patient_id,
        status="generated",
        pdf_url=None,
        created_at=datetime.now()
    )
