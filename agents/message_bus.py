"""
消息总线 - Agent 间通信
借鉴 Agent-Swarm V2.0 架构设计
"""

from typing import Dict, List, Callable, Optional, Any
import logging
from collections import defaultdict
from .base_agent import BaseAgent, AgentMessage


class MessageBus:
    """消息总线 - 负责 Agent 间消息路由"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = logging.getLogger('aimed.message_bus')
        self.message_history: List[AgentMessage] = []
        self.max_history_size = 1000
    
    def register_agent(self, agent: BaseAgent):
        """
        注册 Agent
        
        Args:
            agent: 要注册的 Agent
        """
        if agent.agent_id in self.agents:
            self.logger.warning(f'Agent {agent.agent_id} already registered')
            return
        
        self.agents[agent.agent_id] = agent
        agent.message_bus = self
        self.logger.info(f'Agent registered: {agent.agent_id}')
    
    def unregister_agent(self, agent_id: str):
        """
        取消注册 Agent
        
        Args:
            agent_id: 要取消注册的 Agent ID
        """
        if agent_id in self.agents:
            agent = self.agents.pop(agent_id)
            agent.message_bus = None
            self.logger.info(f'Agent unregistered: {agent_id}')
    
    def subscribe(self, agent_id: str, message_type: str, callback: Callable):
        """
        订阅消息类型
        
        Args:
            agent_id: 订阅者 ID
            message_type: 消息类型
            callback: 回调函数
        """
        key = f'{agent_id}:{message_type}'
        self.subscribers[key].append(callback)
        self.logger.debug(f'Agent {agent_id} subscribed to {message_type}')
    
    def publish(self, message: AgentMessage):
        """
        发布消息
        
        Args:
            message: 要发布的消息
        """
        # 记录消息历史
        self.message_history.append(message)
        if len(self.message_history) > self.max_history_size:
            self.message_history.pop(0)
        
        self.logger.debug(f'Publishing message: {message.sender_id} -> {message.receiver_id} ({message.message_type})')
        
        # 如果指定了接收者，直接发送
        if message.receiver_id:
            if message.receiver_id in self.agents:
                self.agents[message.receiver_id].receive_message(message)
            else:
                self.logger.warning(f'Receiver {message.receiver_id} not found')
        else:
            # 广播消息：发送给所有订阅了该类型的 Agent
            for agent_id in self.agents:
                agent = self.agents[agent_id]
                # 不发送给自己
                if agent_id != message.sender_id:
                    agent.receive_message(message)
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """
        获取 Agent 实例
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent 实例，如果不存在则返回 None
        """
        return self.agents.get(agent_id)
    
    def get_all_agents(self) -> List[BaseAgent]:
        """
        获取所有注册的 Agent
        
        Returns:
            所有 Agent 列表
        """
        return list(self.agents.values())
    
    def get_message_history(self, agent_id: Optional[str] = None, 
                          message_type: Optional[str] = None) -> List[AgentMessage]:
        """
        获取消息历史
        
        Args:
            agent_id: 过滤指定 Agent 的消息（作为发送者或接收者）
            message_type: 过滤指定类型的消息
            
        Returns:
            过滤后的消息列表
        """
        result = self.message_history
        
        if agent_id:
            result = [m for m in result if m.sender_id == agent_id or m.receiver_id == agent_id]
        
        if message_type:
            result = [m for m in result if m.message_type == message_type]
        
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取消息总线统计信息
        
        Returns:
            统计信息字典
        """
        message_types = defaultdict(int)
        for msg in self.message_history:
            message_types[msg.message_type] += 1
        
        return {
            'total_agents': len(self.agents),
            'total_messages': len(self.message_history),
            'message_types': dict(message_types),
            'agents': [agent.get_status() for agent in self.agents.values()]
        }
