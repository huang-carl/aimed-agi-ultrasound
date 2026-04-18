"""
AIMED Conductor Agent - 总指挥智能体

负责：
- 任务调度与路由
- 多 Agent 协同
- 结果整合
- 异常处理
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger
import uuid

class ConductorAgent:
    """
    总指挥 Agent - AIMED Agent Swarm 的协调中枢
    """
    
    def __init__(self):
        self.agent_registry = {}
        self.task_queue = []
        self.completed_tasks = {}
        logger.info("ConductorAgent 初始化完成")
    
    def register_agent(self, agent_name: str, agent_instance: Any):
        """
        注册子 Agent
        """
        self.agent_registry[agent_name] = agent_instance
        logger.info(f"注册 Agent: {agent_name}")
    
    def dispatch_task(self, organs: List[str], image_paths: List[str], patient_id: Optional[str] = None) -> Dict:
        """
        分发诊断任务到对应的器官 Agent
        
        Args:
            organs: 需要诊断的器官列表 ["stomach", "pancreas"]
            image_paths: 影像文件路径列表
            patient_id: 患者 ID（可选）
        
        Returns:
            任务 ID 和状态信息
        """
        task_id = str(uuid.uuid4())
        created_at = datetime.now()
        
        logger.info(f"任务分发：task_id={task_id}, organs={organs}")
        
        # 创建任务记录
        task = {
            "task_id": task_id,
            "status": "processing",
            "organs": organs,
            "image_paths": image_paths,
            "patient_id": patient_id,
            "created_at": created_at,
            "results": {},
            "errors": []
        }
        
        # 验证器官类型
        valid_organs = ["stomach", "pancreas"]
        for organ in organs:
            if organ not in valid_organs:
                task["errors"].append(f"不支持的器官类型：{organ}")
                task["status"] = "failed"
                self.completed_tasks[task_id] = task
                return task
        
        # 调度到对应 Agent（目前为 mock，后续接入真实 Agent）
        for organ in organs:
            if organ in self.agent_registry:
                logger.info(f"调度到 {organ} Agent")
                # TODO: 异步调用 Agent
                # result = await self.agent_registry[organ].diagnose(image_path)
                task["results"][organ] = {"status": "pending"}
            else:
                logger.warning(f"未找到 {organ} Agent，使用默认处理")
                task["results"][organ] = {"status": "no_agent"}
        
        task["status"] = "processing"
        self.task_queue.append(task)
        
        logger.info(f"任务创建成功：{task_id}")
        return task
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """
        查询任务状态
        """
        # 先查进行中任务
        for task in self.task_queue:
            if task["task_id"] == task_id:
                return task
        
        # 再查已完成任务
        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id]
        
        return None
    
    def complete_task(self, task_id: str, results: Dict):
        """
        标记任务完成
        """
        for task in self.task_queue:
            if task["task_id"] == task_id:
                task["status"] = "completed"
                task["results"] = results
                task["completed_at"] = datetime.now()
                self.completed_tasks[task_id] = task
                self.task_queue.remove(task)
                logger.info(f"任务完成：{task_id}")
                return
        
        logger.warning(f"未找到任务：{task_id}")
    
    def get_statistics(self) -> Dict:
        """
        获取统计信息
        """
        return {
            "total_tasks": len(self.task_queue) + len(self.completed_tasks),
            "pending_tasks": len(self.task_queue),
            "completed_tasks": len(self.completed_tasks),
            "registered_agents": list(self.agent_registry.keys())
        }

# 单例实例
conductor_agent = ConductorAgent()
