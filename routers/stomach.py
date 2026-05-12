from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from loguru import logger
import io

from agents.stomach_agent import stomach_agent

router = APIRouter()

class DiagnosisResult(BaseModel):
    organ: str
    disease: str
    probability: float
    suggestion: str
    image_quality: Optional[str] = "good"
    timestamp: datetime
    mode: Optional[str] = "ai"
    model: Optional[str] = None

@router.post("/diagnose", response_model=DiagnosisResult, summary="胃超声影像 AI 诊断")
async def diagnose_stomach(
    file: UploadFile = File(...),
    organ: str = Form("胃"),
    patient_name: str = Form("匿名"),
    patient_age: int = Form(0),
    patient_sex: str = Form("未知"),
    image_description: str = Form("")
):
    """
    胃超声影像 AI 诊断接口
    
    接收上传的超声影像，返回 AI 诊断结果
    """
    logger.info(f"收到胃诊断请求 - 患者：{patient_name}")
    
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
        from agents.base_agent import AgentMessage
        
        message = AgentMessage(
            sender_id="stomach_api",
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
        return DiagnosisResult(
            organ=result.get("organ", "胃"),
            disease=result.get("diagnosis", "待明确"),
            probability=float(result.get("probability", 0.5)),
            suggestion=result.get("suggestion", "建议进一步检查"),
            image_quality=result.get("image_quality", {}).get("level", "good") if isinstance(result.get("image_quality"), dict) else "good",
            timestamp=datetime.fromisoformat(result.get("timestamp", datetime.now().isoformat())),
            mode=result.get("mode", "ai"),
            model=result.get("ai_model", "dashscope")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"诊断异常：{e}")
        # 降级到 Mock
        return DiagnosisResult(
            organ="胃",
            disease="慢性胃炎",
            probability=0.85,
            suggestion="建议结合临床症状，必要时行胃镜检查",
            image_quality="good",
            timestamp=datetime.now(),
            mode="mock"
        )

@router.post("/upload", summary="上传胃超声影像")
async def upload_image(file: UploadFile = File(...)):
    """上传胃超声影像（不立即诊断）"""
    logger.info(f"收到胃影像上传请求：{file.filename}")
    
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
