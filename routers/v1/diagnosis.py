"""
诊断 API v1 - 仅 NVIDIA 模型（Python 3.6 兼容）
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.nvidia_service import NVIDIAClient, DualModelService

router = APIRouter()

# 初始化 NVIDIA 客户端
nvidia_client = None
if os.getenv('NVIDIA_API_KEY'):
    try:
        nvidia_client = NVIDIAClient()
    except Exception as e:
        print(f"NVIDIA 客户端初始化失败：{e}")


class DiagnosisRequest(BaseModel):
    """诊断请求"""
    organ: str  # 器官类型：胃/胰腺
    image_description: str  # 影像描述
    context: Optional[str] = ""  # 额外上下文（病历等）
    model_preference: Optional[str] = "nvidia"  # 模型偏好：nvidia/mock


class DiagnosisResponse(BaseModel):
    """诊断响应"""
    success: bool
    task_id: str
    organ: str
    disease: str
    probability: float
    suggestion: str
    image_quality: str
    mode: str  # 使用的模型：nvidia/mock
    model: Optional[str] = None  # 具体模型名称
    timestamp: datetime
    raw_text: Optional[str] = None  # 原始诊断文本


def mock_diagnose(organ: str, image_description: str) -> Dict[str, Any]:
    """Mock 诊断（降级用）"""
    mock_results = {
        '胃': {
            'disease': '慢性胃炎',
            'probability': 0.85,
            'suggestion': '建议结合临床症状，必要时行胃镜检查'
        },
        '胰腺': {
            'disease': '胰腺回声均匀',
            'probability': 0.92,
            'suggestion': '未见明显异常，建议定期体检'
        }
    }
    
    result = mock_results.get(organ, mock_results['胃'])
    return {
        'organ': organ,
        'disease': result['disease'],
        'probability': result['probability'],
        'suggestion': result['suggestion'],
        'image_quality': 'good',
        'timestamp': datetime.now().isoformat(),
        'mode': 'mock'
    }


@router.post("/diagnose", response_model=DiagnosisResponse, tags=["v1-诊断服务"])
async def diagnose(request: DiagnosisRequest):
    """
    AI 诊断接口 v1（NVIDIA 模型）
    
    支持器官：
    - 胃 (stomach)
    - 胰腺 (pancreas)
    
    降级机制：
    - NVIDIA API 故障时自动降级到 Mock 模式
    """
    try:
        # 验证器官类型
        organ_map = {
            "胃": "胃",
            "stomach": "胃",
            "胰腺": "胰腺",
            "pancreas": "胰腺"
        }
        
        if request.organ not in organ_map:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的器官类型：{request.organ}，支持：胃/stomach/胰腺/pancreas"
            )
        
        organ_cn = organ_map[request.organ]
        
        # 调用 NVIDIA 诊断
        if nvidia_client and request.model_preference != 'mock':
            result = nvidia_client.diagnose(
                organ=organ_cn,
                image_description=request.image_description,
                context=request.context or ""
            )
            
            if result.get('success'):
                return DiagnosisResponse(
                    success=True,
                    task_id=f"diag_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}",
                    organ=organ_cn,
                    disease=result['diagnosis'].get('disease', '待明确诊断'),
                    probability=float(result['diagnosis'].get('probability', 0.8)),
                    suggestion=result['diagnosis'].get('suggestion', '建议进一步检查'),
                    image_quality='good',
                    mode='nvidia',
                    model=result.get('model', 'meta/llama-3.3-70b-instruct'),
                    timestamp=datetime.now(),  # Python 3.6 兼容
                    raw_text=result['diagnosis'].get('raw_text', '')
                )
            else:
                # NVIDIA 失败，降级到 Mock
                print(f"NVIDIA 诊断失败：{result.get('error')}，降级到 Mock")
                mock_result = mock_diagnose(organ_cn, request.image_description)
                return DiagnosisResponse(
                    success=True,  # Mock 成功
                    task_id=f"diag_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}",
                    organ=organ_cn,
                    disease=mock_result['disease'],
                    probability=mock_result['probability'],
                    suggestion=mock_result['suggestion'],
                    image_quality=mock_result['image_quality'],
                    mode='mock',
                    model='mock',
                    timestamp=datetime.now(),
                    raw_text=None
                )
        else:
            # 强制使用 Mock
            mock_result = mock_diagnose(organ_cn, request.image_description)
            return DiagnosisResponse(
                success=True,
                task_id=f"diag_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}",
                organ=organ_cn,
                disease=mock_result['disease'],
                probability=mock_result['probability'],
                suggestion=mock_result['suggestion'],
                image_quality=mock_result['image_quality'],
                mode='mock',
                model='mock',
                timestamp=datetime.now(),
                raw_text=None
            )
        
    except HTTPException:
        raise
    except Exception as e:
        # 未知错误，返回 Mock 结果
        print(f"诊断异常：{str(e)}")
        mock_result = mock_diagnose(organ_cn, request.image_description)
        return DiagnosisResponse(
            success=False,
            task_id=f"diag_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}",
            organ=organ_cn,
            disease="诊断异常",
            probability=0.0,
            suggestion=f"系统异常：{str(e)}，请稍后重试",
            image_quality="unknown",
            mode="error",
            model=None,
            timestamp=datetime.now(),
            raw_text=None
        )


@router.get("/models", tags=["v1-诊断服务"])
async def get_available_models():
    """
    获取可用模型列表
    """
    models = []
    
    # NVIDIA
    if os.getenv('NVIDIA_API_KEY'):
        models.append({
            "name": "NVIDIA Llama-3.3-70B",
            "id": "meta/llama-3.3-70b-instruct",
            "provider": "nvidia",
            "context_length": "1M",
            "status": "available"
        })
    
    # Mock 模式始终可用
    models.append({
        "name": "Mock 模式",
        "id": "mock",
        "provider": "local",
        "context_length": "N/A",
        "status": "available"
    })
    
    return {
        "models": models,
        "routing_mode": "nvidia",
        "mock_mode": os.getenv('MOCK_MODE', 'true').lower() == 'true'
    }
