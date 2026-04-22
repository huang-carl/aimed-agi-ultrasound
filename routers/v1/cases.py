"""
病例管理 API v1
支持病例上传、查询、统计
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.case_database import CaseDatabase
from services.case_storage import CaseStorage
from services.nvidia_service import NVIDIAClient

router = APIRouter()

# 初始化服务
case_db = CaseDatabase()
case_storage = CaseStorage()
nvidia_client = None

if os.getenv('NVIDIA_API_KEY'):
    try:
        nvidia_client = NVIDIAClient()
    except:
        pass


class CaseUploadResponse(BaseModel):
    """病例上传响应"""
    success: bool
    case_id: str
    message: str
    organ: str
    diagnosis: Optional[str] = None
    probability: Optional[float] = None


class CaseInfo(BaseModel):
    """病例信息"""
    id: str
    patient_id: Optional[str] = None
    patient_name: Optional[str] = None
    organ: str
    image_path: str
    diagnosis: Optional[str] = None
    probability: Optional[float] = None
    created_at: str


@router.post("/upload", response_model=CaseUploadResponse, tags=["v1-病例管理"])
async def upload_case(
    organ: str = Form(...),
    patient_id: Optional[str] = Form(None),
    patient_name: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    image_description: Optional[str] = Form(None)
):
    """
    上传病例
    
    - **organ**: 器官类型（胃/胰腺）
    - **patient_id**: 患者 ID（可选）
    - **patient_name**: 患者姓名（可选）
    - **image**: 病例图像（可选）
    - **image_description**: 影像描述（可选）
    """
    # 验证器官类型
    if organ not in ['胃', '胰腺', 'stomach', 'pancreas']:
        raise HTTPException(status_code=400, detail="不支持的器官类型")
    
    organ_cn = '胃' if organ in ['胃', 'stomach'] else '胰腺'
    
    # 生成病例 ID
    case_id = f"case_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    # 保存图像（如果有）
    image_path = ''
    if image:
        image_data = await image.read()
        storage_result = case_storage.save_image(image_data, organ_cn, case_id)
        image_path = storage_result['local_path']
    
    # AI 诊断（如果有影像描述）
    diagnosis = None
    probability = None
    if image_description and nvidia_client:
        try:
            result = nvidia_client.diagnose(organ_cn, image_description)
            if result.get('success'):
                diagnosis = result['diagnosis'].get('disease', '待解析')
                probability = result['diagnosis'].get('probability', 0.8)
        except:
            pass
    
    # 添加到数据库
    case_data = {
        'patient_id': patient_id or '',
        'patient_name': patient_name or '',
        'organ': organ_cn,
        'image_path': image_path,
        'oss_url': '',
        'image_description': image_description or '',
        'diagnosis': diagnosis or '待诊断',
        'probability': probability or 0.0,
        'image_quality': 'good' if image_path else 'unknown',
        'category': datetime.now().strftime('%Y-%m-%d')
    }
    
    case_db.add_case(case_data)
    
    return CaseUploadResponse(
        success=True,
        case_id=case_id,
        message="病例上传成功",
        organ=organ_cn,
        diagnosis=diagnosis,
        probability=probability
    )


@router.get("/list", tags=["v1-病例管理"])
async def list_cases(
    organ: Optional[str] = None,
    limit: int = 100
):
    """
    获取病例列表
    
    - **organ**: 器官类型（可选）
    - **limit**: 返回数量限制
    """
    if organ:
        organ_cn = '胃' if organ in ['胃', 'stomach'] else '胰腺'
        cases = case_db.get_cases_by_organ(organ_cn, limit)
    else:
        cases = case_db.list_all_cases()[:limit]
    
    return {
        'count': len(cases),
        'cases': cases
    }


@router.get("/{case_id}", tags=["v1-病例管理"])
async def get_case(case_id: str):
    """获取单个病例详情"""
    case = case_db.get_case(case_id)
    
    if not case:
        raise HTTPException(status_code=404, detail="病例不存在")
    
    return case


@router.get("/stats/statistics", tags=["v1-病例管理"])
async def get_statistics():
    """获取病例统计信息"""
    stats = case_db.get_statistics()
    storage_stats = case_storage.get_storage_stats()
    
    return {
        **stats,
        'storage': storage_stats
    }


@router.get("/export/report", tags=["v1-病例管理"])
async def export_report():
    """导出病例报告"""
    report_path = case_db.export_report()
    
    return {
        'success': True,
        'report_path': report_path,
        'message': '报告已导出'
    }


@router.get("/storage/stats", tags=["v1-病例管理"])
async def get_storage_statistics():
    """获取存储统计信息"""
    stats = case_storage.get_storage_stats()
    return stats
