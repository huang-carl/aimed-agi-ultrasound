"""
诊断 API v2 - V2.0 架构
通过 Orchestrator + Agent 处理诊断请求
支持多模型路由（NVIDIA / DashScope / Mock）
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import os

from agents.conductor_agent import conductor_agent
from agents.stomach_agent import stomach_agent
from agents.pancreas_agent import pancreas_agent
from agents.base_agent import AgentMessage

router = APIRouter()


class DiagnosisRequest(BaseModel):
    """诊断请求"""
    organ: str  # 器官类型：胃/胰腺
    image_description: str  # 影像描述
    context: Optional[str] = ""  # 额外上下文（病历等）
    model_preference: Optional[str] = "nvidia"  # 模型偏好：nvidia/mock
    filling_status: Optional[str] = "已充盈"  # 充盈状态


class DiagnosisResponse(BaseModel):
    """诊断响应"""
    success: bool
    task_id: str
    organ: str
    disease: str
    probability: float
    suggestion: str
    image_quality: str
    mode: str
    model: Optional[str] = None
    timestamp: str
    raw_text: Optional[str] = None
    agent_version: str = "2.0"


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
    AI 诊断接口 v2 (V2.0 架构)
    
    通过 Orchestrator + Agent 处理诊断请求
    支持器官：胃 (stomach) / 胰腺 (pancreas)
    降级机制：NVIDIA → DashScope → Mock
    """
    try:
        organ_map = {
            "胃": "胃", "stomach": "胃",
            "胰腺": "胰腺", "pancreas": "胰腺"
        }
        
        if request.organ not in organ_map:
            raise HTTPException(status_code=400,
                detail=f"不支持的器官类型：{request.organ}")
        
        organ_cn = organ_map[request.organ]
        
        # 检查充盈状态
        if request.filling_status != "已充盈":
            return DiagnosisResponse(
                success=False,
                task_id=f"diag_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}",
                organ=organ_cn,
                disease="无法诊断",
                probability=0.0,
                suggestion="未充盈状态下无法进行诊断，请口服造影剂后重新检查",
                image_quality="unknown",
                mode="rejected",
                model=None,
                timestamp=datetime.now().isoformat(),
                raw_text=None
            )
        
        # 通过对应 Agent 处理诊断
        agent_map = {"胃": stomach_agent, "胰腺": pancreas_agent}
        agent = agent_map.get(organ_cn)
        
        if not agent:
            raise HTTPException(status_code=400, detail=f"未找到 {organ_cn} 诊断 Agent")
        
        # 构建诊断消息
        message = AgentMessage(
            sender_id="diagnosis_api",
            receiver_id=agent.agent_id,
            message_type="diagnose",
            payload={
                "image_data": None,  # 文本描述模式，无图像
                "image_format": "text",
                "image_description": request.image_description,
                "context": request.context or ""
            }
        )
        
        response = await agent.process(message)
        
        if response.message_type == "error":
            # Agent 失败，降级到 Mock
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
                timestamp=datetime.now().isoformat(),
                raw_text=None
            )
        
        result = response.payload
        mode = result.get('mode', 'agent_v2')
        model_name = result.get('ai_model', f"{agent.agent_id}_v2.0")
        
        return DiagnosisResponse(
            success=True,
            task_id=f"diag_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}",
            organ=result.get("organ", organ_cn),
            disease=result.get("diagnosis", "待明确诊断"),
            probability=result.get("probability", 0.8),
            suggestion=result.get("suggestion", "建议进一步检查"),
            image_quality=result.get("image_quality", {}).get("level", "good") if isinstance(result.get("image_quality"), dict) else "good",
            mode=mode,
            model=model_name,
            timestamp=datetime.now().isoformat(),
            raw_text=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
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
            timestamp=datetime.now().isoformat(),
            raw_text=None
        )


@router.get("/models", tags=["v1-诊断服务"])
async def get_available_models():
    """获取可用模型/Agent 列表"""
    models = [
        {
            "name": "Stomach Agent V2.0",
            "id": "stomach_v2",
            "provider": "local",
            "capabilities": ["stomach_diagnosis", "image_quality_check", "lesion_detection"],
            "status": "available"
        },
        {
            "name": "Pancreas Agent V2.0",
            "id": "pancreas_v2",
            "provider": "local",
            "capabilities": ["pancreas_diagnosis", "image_quality_check", "organ_segmentation", "risk_prediction"],
            "status": "available"
        },
        {
            "name": "Report Agent V2.0",
            "id": "report_v2",
            "provider": "local",
            "capabilities": ["report_generation", "multi_language_support", "pdf_export"],
            "status": "available"
        }
    ]
    
    if os.getenv('NVIDIA_API_KEY'):
        models.append({
            "name": "NVIDIA Llama-3.3-70B",
            "id": "meta/llama-3.3-70b-instruct",
            "provider": "nvidia",
            "context_length": "1M",
            "status": "available"
        })
    
    return {
        "models": models,
        "architecture": "V2.0 (Agent Swarm)",
        "agents_registered": len(conductor_agent.agent_registry) + 3  # +3 for stomach/pancreas/report
    }
