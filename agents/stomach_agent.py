"""
AIMED Stomach Agent - 胃诊断智能体

负责：
- 胃超声影像 AI 诊断
- 病灶识别
- 诊断建议生成
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger

from .base_agent import SupportAgent, AgentMessage


class StomachAgent(SupportAgent):
    """
    胃诊断 Agent - 专注于胃部超声影像的 AI 诊断
    继承 SupportAgent 基类
    """
    
    def __init__(self):
        config = {
            'agent_name': 'Stomach Agent',
            'agent_version': '2.0.0',
            'description': '胃诊断 Agent - 专注于胃部超声影像的 AI 诊断'
        }
        super().__init__(agent_id="stomach", config=config)
        self.model_path = None
        self.diagnosis_count = 0
        logger.info("StomachAgent 初始化完成 (V2.0 架构)")
    
    def load_model(self, model_path: str):
        """
        加载胃诊断模型
        """
        self.model_path = model_path
        logger.info(f"加载胃诊断模型：{model_path}")
        # TODO: 实际加载模型逻辑
        # self.model = torch.load(model_path)
    
    def diagnose(self, image_data: bytes, image_format: str = "png", 
                 image_description: str = "", context: str = "") -> Dict[str, Any]:
        """
        执行胃超声影像诊断
        
        Args:
            image_data: 影像二进制数据
            image_format: 影像格式（png/jpg/dicom）
            image_description: 影像描述（文本模式）
            context: 临床上下文
        
        Returns:
            诊断结果字典
        """
        self.diagnosis_count += 1
        logger.info(f"执行胃诊断，第 {self.diagnosis_count} 例")
        
        # 尝试使用 AI 诊断服务（多提供商自动切换）
        ai_result = None
        if image_description:
            try:
                from services.ai_diagnosis_service import ai_diagnosis_service
                ai_result = ai_diagnosis_service.diagnose(
                    organ="胃",
                    image_description=image_description,
                    context=context
                )
                
                if ai_result.get('success'):
                    diag = ai_result['diagnosis']
                    result = {
                        "organ": "胃",
                        "timestamp": datetime.now().isoformat(),
                        "image_quality": {
                            "score": 0.88,
                            "level": "good",
                            "clarity": 0.90,
                            "filling": 0.85
                        },
                        "findings": diag.get('findings', []),
                        "diagnosis": diag.get('disease', '待明确'),
                        "probability": float(diag.get('probability', 0.8)),
                        "suggestion": diag.get('suggestion', '建议进一步检查'),
                        "risk_level": diag.get('risk_level', 'unknown'),
                        "ai_model": ai_result.get('model', 'dashscope'),
                        "mode": "ai"
                    }
                    logger.info(f"✅ AI 诊断完成：{result['diagnosis']}, 置信度：{result['probability']}")
                    return result
                else:
                    logger.warning(f"AI 诊断失败，降级到 Mock：{ai_result.get('error')}")
            except Exception as e:
                logger.error(f"AI 诊断异常：{e}，降级到 Mock")
        
        # 降级到 Mock 数据
        result = {
            "organ": "胃",
            "timestamp": datetime.now().isoformat(),
            "image_quality": {
                "score": 0.88,
                "level": "good",
                "clarity": 0.90,
                "filling": 0.85
            },
            "findings": [
                {
                    "type": "黏膜隆起",
                    "location": "胃体部",
                    "size": "6mm×5mm",
                    "confidence": 0.85,
                    "description": "胃体部可见一隆起性病变，边界尚清"
                }
            ],
            "diagnosis": "慢性胃炎伴黏膜隆起",
            "probability": 0.85,
            "suggestion": "建议结合临床症状，必要时行胃镜检查",
            "risk_level": "low",
            "mode": "mock"
        }
        
        logger.info(f"胃诊断完成（Mock）：{result['diagnosis']}, 置信度：{result['probability']}")
        
        return result
    
    def quality_check(self, image_data: bytes) -> Dict[str, Any]:
        """
        影像质量评估
        """
        logger.info("执行胃影像质量评估")
        
        # TODO: 实际质量评估逻辑
        result = {
            "passed": True,
            "score": 0.88,
            "dimensions": {
                "clarity": 0.90,
                "contrast": 0.85,
                "completeness": 0.92,
                "artifact": 0.88
            },
            "suggestions": []
        }
        
        return result
    
    async def process(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        处理消息（实现 SupportAgent 抽象方法）
        
        Args:
            message: 输入消息
            
        Returns:
            响应消息
        """
        try:
            payload = message.payload
            
            # 根据消息类型路由
            if message.message_type == 'diagnose':
                # 执行诊断
                image_data = payload.get('image_data')
                image_format = payload.get('image_format', 'png')
                image_description = payload.get('image_description', '')
                context = payload.get('context', '')
                
                result = self.diagnose(image_data, image_format, image_description, context)
                
                return AgentMessage(
                    sender_id=self.agent_id,
                    receiver_id=message.sender_id,
                    message_type='diagnosis_result',
                    payload=result
                )
            
            elif message.message_type == 'quality_check':
                # 质量检查
                image_data = payload.get('image_data')
                result = self.quality_check(image_data)
                
                return AgentMessage(
                    sender_id=self.agent_id,
                    receiver_id=message.sender_id,
                    message_type='quality_result',
                    payload=result
                )
            
            elif message.message_type == 'status':
                # 状态查询
                return AgentMessage(
                    sender_id=self.agent_id,
                    receiver_id=message.sender_id,
                    message_type='status_response',
                    payload=self.get_statistics()
                )
            
            else:
                return AgentMessage(
                    sender_id=self.agent_id,
                    receiver_id=message.sender_id,
                    message_type='error',
                    payload={'error': f'未知消息类型：{message.message_type}'}
                )
                
        except Exception as e:
            logger.error(f"StomachAgent 处理消息失败：{e}")
            return AgentMessage(
                sender_id=self.agent_id,
                receiver_id=message.sender_id,
                message_type='error',
                payload={'error': str(e)}
            )
    
    def get_capabilities(self) -> List[str]:
        """
        返回 Agent 的能力列表（实现 BaseAgent 抽象方法）
        """
        return ['stomach_diagnosis', 'image_quality_check', 'lesion_detection']
    
    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行支撑任务（实现 SupportAgent 抽象方法）
        """
        task_type = task_data.get('task_type', 'diagnose')
        
        if task_type == 'diagnose':
            return self.diagnose(
                task_data.get('image_data'),
                task_data.get('image_format', 'png')
            )
        elif task_type == 'quality_check':
            return self.quality_check(task_data.get('image_data'))
        else:
            return {'error': f'未知任务类型：{task_type}'}
    
    def get_statistics(self) -> Dict:
        """
        获取统计信息
        """
        return {
            "total_diagnoses": self.diagnosis_count,
            "model_loaded": self.model_path is not None,
            "agent_type": "stomach",
            "agent_id": self.agent_id,
            "agent_version": self.config.get('agent_version', '2.0.0')
        }

# 单例实例
stomach_agent = StomachAgent()
