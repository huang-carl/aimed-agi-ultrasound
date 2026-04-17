from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from loguru import logger
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
import os

router = APIRouter()

class DiagnosisItem(BaseModel):
    organ: str
    disease: str
    probability: float
    suggestion: str

class ReportRequest(BaseModel):
    patient_id: str
    patient_name: Optional[str] = "匿名"
    patient_gender: Optional[str] = "未知"
    patient_age: Optional[int] = 0
    doctor_id: Optional[str] = ""
    doctor_name: Optional[str] = ""
    diagnosis_results: List[DiagnosisItem]
    image_quality: Optional[str] = "good"

class ReportResponse(BaseModel):
    report_id: str
    status: str
    pdf_path: Optional[str] = None
    created_at: datetime

@router.post("/generate", response_model=ReportResponse, summary="生成诊断报告")
async def generate_report(request: ReportRequest):
    """
    根据诊断结果生成结构化报告
    
    **输入：**
    - patient_id: 患者 ID
    - patient_name: 患者姓名
    - diagnosis_results: 诊断结果列表
    - doctor_id: 医生 ID
    - doctor_name: 医生姓名
    
    **输出：**
    - report_id: 报告 ID
    - status: 生成状态
    - pdf_path: PDF 文件路径
    """
    logger.info(f"收到报告生成请求：患者 {request.patient_id}")
    
    report_id = f"RPT_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    pdf_dir = "data/reports"
    
    # 确保目录存在
    os.makedirs(pdf_dir, exist_ok=True)
    
    pdf_path = f"{pdf_dir}/{report_id}.pdf"
    
    try:
        # 创建 PDF
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        
        # 标题
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width / 2, height - 50, "AIMED 超声造影诊断报告")
        
        # 基本信息
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 100, f"报告 ID: {report_id}")
        c.drawString(50, height - 120, f"患者 ID: {request.patient_id}")
        c.drawString(50, height - 140, f"患者姓名：{request.patient_name}")
        c.drawString(300, height - 120, f"性别：{request.patient_gender}")
        c.drawString(300, height - 140, f"年龄：{request.patient_age}")
        c.drawString(50, height - 160, f"检查日期：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        c.drawString(300, height - 160, f"检查医生：{request.doctor_name}")
        
        # 诊断结果
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 200, "诊断结果")
        
        c.setFont("Helvetica", 11)
        y_position = height - 230
        for item in request.diagnosis_results:
            c.drawString(50, y_position, f"器官：{item.organ}")
            y_position -= 20
            c.drawString(50, y_position, f"诊断：{item.disease} (置信度：{item.probability:.1%})")
            y_position -= 20
            c.drawString(50, y_position, f"建议：{item.suggestion}")
            y_position -= 40
        
        # 免责声明
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(50, 80, "免责声明：本报告由 AI 辅助生成，仅供医生参考，最终诊断请以执业医师判断为准。")
        
        # 页脚
        c.drawString(50, 50, f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(400, 50, f"页码：1/1")
        
        c.save()
        
        logger.info(f"报告生成成功：{pdf_path}")
        
        return ReportResponse(
            report_id=report_id,
            status="success",
            pdf_path=pdf_path,
            created_at=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"报告生成失败：{str(e)}")
        raise HTTPException(status_code=500, detail=f"报告生成失败：{str(e)}")

@router.get("/{report_id}", summary="获取报告信息")
async def get_report(report_id: str):
    """
    获取报告信息
    """
    pdf_path = f"data/reports/{report_id}.pdf"
    
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="报告不存在")
    
    return {
        "report_id": report_id,
        "pdf_path": pdf_path,
        "created_at": datetime.fromtimestamp(os.path.getctime(pdf_path))
    }

@router.get("/health", summary="报告服务健康检查")
async def health_check():
    return {"status": "ok", "service": "Report Generation"}
