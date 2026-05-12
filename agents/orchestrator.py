"""
Agent 编排器 - 负责协调所有 Agent 的工作
借鉴 Agent-Swarm V2.0 架构设计
"""

import asyncio
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import uuid

from .base_agent import BaseAgent, AgentMessage, DiagnosticAgent, SupportAgent
from .message_bus import MessageBus


class AgentOrchestrator:
    """Agent 编排器 - 系统的核心控制器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化编排器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.message_bus = MessageBus()
        self.logger = logging.getLogger('aimed.orchestrator')
        self.is_running = False
        self.workflows: Dict[str, Dict[str, Any]] = {}  # workflow_id -> workflow definition
        self.active_tasks: Dict[str, Dict[str, Any]] = {}  # task_id -> task info
        
    def register_agent(self, agent: BaseAgent):
        """
        注册 Agent
        
        Args:
            agent: 要注册的 Agent
        """
        self.message_bus.register_agent(agent)
        self.logger.info(f'Agent {agent.agent_id} registered to orchestrator')
    
    def unregister_agent(self, agent_id: str):
        """
        取消注册 Agent
        
        Args:
            agent_id: Agent ID
        """
        self.message_bus.unregister_agent(agent_id)
        self.logger.info(f'{agent_id} unregistered from orchestrator')
    
    def create_workflow(self, name: str, agent_sequence: List[str], 
                        description: str = "") -> str:
        """
        创建工作流
        
        Args:
            name: 工作流名称
            agent_sequence: Agent ID 序列，定义执行顺序
            description: 工作流描述
            
        Returns:
            工作流 ID
        """
        workflow_id = str(uuid.uuid4())
        self.workflows[workflow_id] = {
            'name': name,
            'description': description,
            'agent_sequence': agent_sequence,
            'created_at': datetime.now().isoformat(),
            'execution_count': 0
        }
        self.logger.info(f'Workflow created: {name} (ID: {workflow_id})')
        return workflow_id
    
    async def execute_workflow(self, workflow_id: str, 
                               initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行工作流
        
        Args:
            workflow_id: 工作流 ID
            initial_data: 初始数据
            
        Returns:
            执行结果
        """
        if workflow_id not in self.workflows:
            raise ValueError(f'Workflow {workflow_id} not found')
        
        workflow = self.workflows[workflow_id]
        agent_sequence = workflow['agent_sequence']
        
        self.logger.info(f'Executing workflow: {workflow["name"]}')
        
        # 创建任务
        task_id = str(uuid.uuid4())
        self.active_tasks[task_id] = {
            'workflow_id': workflow_id,
            'start_time': datetime.now(),
            'status': 'running',
            'current_step': 0,
            'results': []
        }
        
        # 依次执行 Agent
        current_data = initial_data
        for idx, agent_id in enumerate(agent_sequence):
            self.logger.debug(f'Step {idx+1}/{len(agent_sequence)}: {agent_id}')
            
            # 获取 Agent
            agent = self.message_bus.get_agent(agent_id)
            if not agent:
                error_msg = f'Agent {agent_id} not found'
                self.logger.error(error_msg)
                self.active_tasks[task_id]['status'] = 'failed'
                return {'task_id': task_id, 'error': error_msg}
            
            # 创建消息
            message = AgentMessage(
                sender_id='orchestrator',
                receiver_id=agent_id,
                message_type='task',
                payload=current_data
            )
            
            # 处理消息
            try:
                response = await agent.process(message)
                if response:
                    current_data = response.payload
                    self.active_tasks[task_id]['results'].append({
                        'agent_id': agent_id,
                        'result': current_data,
                        'status': 'success'
                    })
                else:
                    self.active_tasks[task_id]['results'].append({
                        'agent_id': agent_id,
                        'result': None,
                        'status': 'success_no_response'
                    })
            except Exception as e:
                error_msg = f'Error in agent {agent_id}: {str(e)}'
                self.logger.error(error_msg, exc_info=True)
                self.active_tasks[task_id]['results'].append({
                    'agent_id': agent_id,
                    'error': error_msg,
                    'status': 'failed'
                })
                self.active_tasks[task_id]['status'] = 'failed'
                return {'task_id': task_id, 'error': error_msg}
            
            self.active_tasks[task_id]['current_step'] = idx + 1
        
        # 完成
        self.active_tasks[task_id]['status'] = 'completed'
        self.active_tasks[task_id]['end_time'] = datetime.now().isoformat()
        workflow['execution_count'] += 1
        
        self.logger.info(f'Workflow completed: {workflow["name"]} (Task ID: {task_id})')
        
        return {
            'task_id': task_id,
            'status': 'completed',
            'result': current_data,
            'steps_executed': len(agent_sequence)
        }
    
    async def execute_agent(self, agent_id: str, 
                            input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行单个 Agent
        
        Args:
            agent_id: Agent ID
            input_data: 输入数据
            
        Returns:
            执行结果
        """
        agent = self.message_bus.get_agent(agent_id)
        if not agent:
            raise ValueError(f'Agent {agent_id} not found')
        
        message = AgentMessage(
            sender_id='orchestrator',
            receiver_id=agent_id,
            message_type='task',
            payload=input_data
        )
        
        try:
            response = await agent.process(message)
            return {
                'status': 'success',
                'agent_id': agent_id,
                'result': response.payload if response else None
            }
        except Exception as e:
            self.logger.error(f'Error executing agent {agent_id}: {e}', exc_info=True)
            return {
                'status': 'failed',
                'agent_id': agent_id,
                'error': str(e)
            }
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        获取工作流定义
        
        Args:
            workflow_id: 工作流 ID
            
        Returns:
            工作流定义，如果不存在则返回 None
        """
        return self.workflows.get(workflow_id)
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """
        列出所有工作流
        
        Returns:
            工作流列表
        """
        return [
            {'workflow_id': wid, **wdef}
            for wid, wdef in self.workflows.items()
        ]
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务状态
        
        Args:
            task_id: 任务 ID
            
        Returns:
            任务状态，如果不存在则返回 None
        """
        return self.active_tasks.get(task_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取编排器统计信息
        
        Returns:
            统计信息字典
        """
        return {
            'total_agents': len(self.message_bus.agents),
            'total_workflows': len(self.workflows),
            'active_tasks': len([t for t in self.active_tasks.values() 
                               if t['status'] == 'running']),
            'completed_tasks': len([t for t in self.active_tasks.values() 
                                   if t['status'] == 'completed']),
            'failed_tasks': len([t for t in self.active_tasks.values() 
                                if t['status'] == 'failed']),
            'message_bus_stats': self.message_bus.get_statistics()
        }
    
    def start(self):
        """启动编排器"""
        self.is_running = True
        self.logger.info('Agent Orchestrator started')
    
    def stop(self):
        """停止编排器"""
        self.is_running = False
        # 停止所有 Agent
        for agent in self.message_bus.get_all_agents():
            agent.stop()
        self.logger.info('Agent Orchestrator stopped')
    
    def initialize_default_workflows(self):
        """初始化默认工作流"""
        
        # 工作流 1: 胃诊断流程
        self.create_workflow(
            name='胃诊断完整流程',
            agent_sequence=[
                'ImagePreprocessor',
                'StomachAnalyzer',
                'FeatureExtractor',
                'DiagnosisGenerator',
                'QualityChecker'
            ],
            description='完整的胃影像诊断流程：预处理 → 分析 → 特征提取 → 诊断生成 → 质控'
        )
        
        # 工作流 2: 胰腺诊断流程
        self.create_workflow(
            name='胰腺诊断完整流程',
            agent_sequence=[
                'ImagePreprocessor',
                'PancreasAnalyzer',
                'FeatureExtractor',
                'DiagnosisGenerator',
                'QualityChecker'
            ],
            description='完整的胰腺影像诊断流程'
        )
        
        # 工作流 3: 风险分析流程
        self.create_workflow(
            name='风险分析流程',
            agent_sequence=[
                'RiskStratifier',
                'TrendAnalyzer',
                'MultiDisciplinary'
            ],
            description='患者风险分层和分析'
        )
        
        self.logger.info('Default workflows initialized')
