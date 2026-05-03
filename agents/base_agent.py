"""
AIMED Agent Swarm - 核心框架
Agent 基类定义
借鉴 Agent-Swarm V2.0 架构设计
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging
import uuid

@dataclass
class AgentMessage:
    """Agent 间通信消息"""
    sender_id: str
    receiver_id: Optional[str]  # None 表示广播
    message_type: str  # 'task', 'result', 'error', 'status'
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'message_id': self.message_id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'message_type': self.message_type,
            'payload': self.payload,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMessage':
        return cls(
            sender_id=data['sender_id'],
            receiver_id=data.get('receiver_id'),
            message_type=data['message_type'],
            payload=data['payload'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            message_id=data['message_id']
        )


class BaseAgent(ABC):
    """Agent 基类 - 所有 Agent 都应继承此类"""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        """
        初始化 Agent
        
        Args:
            agent_id: Agent 唯一标识符
            config: Agent 配置字典
        """
        self.agent_id = agent_id
        self.config = config
        self.logger = logging.getLogger(f'aimed.agent.{agent_id}')
        self.message_bus = None  # 将在注册时设置
        self.is_running = False
        self.task_queue: List[AgentMessage] = []
        
    @abstractmethod
    async def process(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        处理接收到的消息 - 必须由子类实现
        
        Args:
            message: 接收到的消息
            
        Returns:
            处理结果消息，如果不需要回复则返回 None
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        返回 Agent 的能力列表
        
        Returns:
            能力列表，例如 ['image_analysis', 'diagnosis_generation']
        """
        pass
    
    def start(self):
        """启动 Agent"""
        self.is_running = True
        self.logger.info(f'Agent {self.agent_id} started')
    
    def stop(self):
        """停止 Agent"""
        self.is_running = False
        self.logger.info(f'Agent {self.agent_id} stopped')
    
    def send_message(self, receiver_id: Optional[str], message_type: str, 
                    payload: Dict[str, Any]) -> AgentMessage:
        """
        发送消息
        
        Args:
            receiver_id: 接收者 ID，None 表示广播
            message_type: 消息类型
            payload: 消息负载
            
        Returns:
            创建的消息对象
        """
        message = AgentMessage(
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            message_type=message_type,
            payload=payload
        )
        
        if self.message_bus:
            self.message_bus.publish(message)
            self.logger.debug(f'Sent message to {receiver_id}: {message_type}')
        
        return message
    
    def receive_message(self, message: AgentMessage):
        """
        接收消息 - 由消息总线调用
        
        Args:
            message: 接收到的消息
        """
        self.task_queue.append(message)
        self.logger.debug(f'Received message from {message.sender_id}: {message.message_type}')
    
    async def process_queue(self):
        """处理消息队列中的所有消息"""
        while self.task_queue:
            message = self.task_queue.pop(0)
            try:
                response = await self.process(message)
                if response and self.message_bus:
                    self.message_bus.publish(response)
            except Exception as e:
                self.logger.error(f'Error processing message: {e}', exc_info=True)
                # 发送错误消息
                if self.message_bus:
                    error_message = AgentMessage(
                        sender_id=self.agent_id,
                        receiver_id=message.sender_id,
                        message_type='error',
                        payload={'error': str(e), 'original_message_id': message.message_id}
                    )
                    self.message_bus.publish(error_message)
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取 Agent 状态
        
        Returns:
            状态字典
        """
        return {
            'agent_id': self.agent_id,
            'is_running': self.is_running,
            'queue_size': len(self.task_queue),
            'capabilities': self.get_capabilities()
        }
    
    def __str__(self):
        return f'{self.__class__.__name__}(id={self.agent_id})'
    
    def __repr__(self):
        return self.__str__()


class DiagnosticAgent(BaseAgent):
    """诊断类 Agent 基类"""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, config)
        self.diagnosis_count = 0
        self.accuracy_sum = 0.0
    
    @abstractmethod
    async def analyze_image(self, image_data: Any) -> Dict[str, Any]:
        """
        分析医学影像
        
        Args:
            image_data: 影像数据
            
        Returns:
            分析结果字典
        """
        pass
    
    def generate_diagnosis_report(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成诊断报告
        
        Args:
            analysis_result: 分析结果
            
        Returns:
            诊断报告字典
        """
        report = {
            'diagnosis_id': f'diag_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'agent_id': self.agent_id,
            'timestamp': datetime.now().isoformat(),
            'result': analysis_result,
            'confidence': analysis_result.get('confidence', 0.0)
        }
        self.diagnosis_count += 1
        return report
    
    def update_accuracy(self, predicted: Any, actual: Any):
        """
        更新准确率统计
        
        Args:
            predicted: 预测结果
            actual: 实际结果
        """
        is_correct = predicted == actual
        self.accuracy_sum += 1.0 if is_correct else 0.0
    
    def get_accuracy(self) -> float:
        """
        获取当前准确率
        
        Returns:
            准确率 (0-1)
        """
        if self.diagnosis_count == 0:
            return 0.0
        return self.accuracy_sum / self.diagnosis_count
    
    def get_status(self) -> Dict[str, Any]:
        status = super().get_status()
        status.update({
            'diagnosis_count': self.diagnosis_count,
            'accuracy': self.get_accuracy()
        })
        return status


class SupportAgent(BaseAgent):
    """支撑类 Agent 基类"""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, config)
        self.task_count = 0
    
    @abstractmethod
    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行支撑任务
        
        Args:
            task_data: 任务数据
            
        Returns:
            执行结果
        """
        pass
    
    def get_status(self) -> Dict[str, Any]:
        status = super().get_status()
        status.update({
            'task_count': self.task_count
        })
        return status
