from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from loguru import logger
import io

router = APIRouter()

class DiagnosisResult(BaseModel):
    organ: str
    disease: str
    probability: float
    suggestion: str
    image_quality: Optional[str] = "good"
    timestamp: datetime

@router.post("/diagnose", response_model=DiagnosisResult, summary="胃超声影像 AI 诊断")
async def diagnose_stomach(file: UploadFile = File(...)):
    """
    胃超声影像 AI 诊断接口
    
    接收上传的超声影像，返回 AI 诊断结果
    
    **输入：**
    - file: 超声影像文件（支持 JPG/PNG/DICOM）
    
    **输出：**
    - organ: 器官名称（胃）
    - disease: 疾病类别
    - probability: 置信度分数（0-1）
    - suggestion: 诊疗建议
    - image_quality: 图像质量评估
    """
    logger.info("收到胃诊断请求")
    
    # 验证文件类型
    allowed_types = ["image/jpeg", "image/png", "application/dicom"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型：{file.content_type}，支持：{allowed_types}"
        )
    
    # 读取文件
    try:
        img_bytes = await file.read()
        if len(img_bytes) == 0:
            raise HTTPException(status_code=400, detail="文件为空")
        
        logger.info(f"文件读取成功，大小：{len(img_bytes)} bytes")
    except Exception as e:
        logger.error(f"文件读取失败：{str(e)}")
        raise HTTPException(status_code=500, detail="文件读取失败")
    
    # TODO: 调用胃诊断 AI 模型
    # 目前使用 mock 数据演示
    result = DiagnosisResult(
        organ="胃",
        disease="慢性胃炎",
        probability=0.85,
        suggestion="建议结合临床症状，必要时行胃镜检查",
        image_quality="good",
        timestamp=datetime.now()
    )
    
    logger.info(f"胃诊断完成：{result.disease}, 置信度：{result.probability}")
    
    return result

@router.post("/upload", summary="上传胃超声影像")
async def upload_image(file: UploadFile = File(...)):
    """
    上传胃超声影像（不立即诊断）
    """
    logger.info(f"收到胃影像上传请求：{file.filename}")
    
    # 保存文件（生产环境应保存到对象存储）
    try:
        content = await file.read()
        file_path = f"data/samples/stomach_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"文件保存成功：{file_path}")
        
        return {
            "status": "success",
            "file_path": file_path,
            "size": len(content)
        }
    except Exception as e:
        logger.error(f"文件保存失败：{str(e)}")
        raise HTTPException(status_code=500, detail="文件保存失败")

@router.get("/health", summary="胃诊断服务健康检查")
async def health_check():
    return {"status": "ok", "service": "Stomach Diagnosis"}
