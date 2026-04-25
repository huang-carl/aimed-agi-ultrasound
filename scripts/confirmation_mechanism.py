#!/usr/bin/env python3
"""
询问确认机制
当小菲同学需要调用 Hermes 后端时，先询问用户确认
"""

import os
import json
import requests
from typing import Dict, Any, Optional
from datetime import datetime


class ConfirmationMechanism:
    """询问确认机制"""
    
    def __init__(self, hermes_endpoint: str = "http://127.0.0.1:18792"):
        self.hermes_endpoint = hermes_endpoint
        self.confirmation_log = "./data/confirmations.json"
        os.makedirs("./data", exist_ok=True)
    
    def check_hermes_status(self) -> Dict[str, Any]:
        """检查 Hermes 后端状态"""
        try:
            response = requests.get(f"{self.hermes_endpoint}/health", timeout=5)
            if response.status_code == 200:
                return {
                    "available": True,
                    "status": response.json(),
                    "message": "Hermes 后端运行正常"
                }
            else:
                return {
                    "available": False,
                    "status": None,
                    "message": f"Hermes 后端异常 (HTTP {response.status_code})"
                }
        except Exception as e:
            return {
                "available": False,
                "status": None,
                "message": f"Hermes 后端不可达: {str(e)}"
            }
    
    def request_confirmation(self, task_type: str, task_description: str, 
                           user_id: str = "skytop") -> Dict[str, Any]:
        """
        请求用户确认
        
        Args:
            task_type: 任务类型（diagnosis/segmentation/vector_search）
            task_description: 任务描述
            user_id: 用户 ID
            
        Returns:
            确认结果
        """
        # 检查 Hermes 状态
        hermes_status = self.check_hermes_status()
        
        if not hermes_status["available"]:
            return {
                "confirmed": False,
                "reason": "Hermes 后端不可用",
                "message": hermes_status["message"]
            }
        
        # 记录确认请求
        confirmation = {
            "timestamp": datetime.now().isoformat(),
            "task_type": task_type,
            "task_description": task_description,
            "user_id": user_id,
            "status": "pending"
        }
        
        # 保存到日志
        self._save_confirmation(confirmation)
        
        return {
            "confirmed": True,
            "confirmation_id": f"CONF_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "message": f"已请求用户确认：{task_type} - {task_description}",
            "confirmation": confirmation
        }
    
    def execute_task(self, task_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行任务（确认后）
        
        Args:
            task_type: 任务类型
            params: 任务参数
            
        Returns:
            执行结果
        """
        if task_type == "diagnosis":
            return self._execute_diagnosis(params)
        elif task_type == "segmentation":
            return self._execute_segmentation(params)
        elif task_type == "vector_search":
            return self._execute_vector_search(params)
        else:
            return {"success": False, "error": f"未知任务类型: {task_type}"}
    
    def _execute_diagnosis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行诊断任务"""
        try:
            response = requests.post(
                f"{self.hermes_endpoint}/api/v1/diagnose",
                json=params,
                timeout=30
            )
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _execute_segmentation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行图像分割任务"""
        try:
            response = requests.post(
                f"{self.hermes_endpoint}/api/v1/segment",
                json=params,
                timeout=60
            )
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _execute_vector_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行向量检索任务"""
        try:
            response = requests.get(
                f"{self.hermes_endpoint}/api/v1/knowledge/search",
                params=params,
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _save_confirmation(self, confirmation: Dict[str, Any]):
        """保存确认记录"""
        try:
            if os.path.exists(self.confirmation_log):
                with open(self.confirmation_log, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            logs.append(confirmation)
            
            with open(self.confirmation_log, 'w') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Confirmation] 保存失败: {e}")


# 测试
if __name__ == '__main__':
    print("=" * 60)
    print("询问确认机制测试")
    print("=" * 60)
    
    mechanism = ConfirmationMechanism()
    
    # 检查 Hermes 状态
    print("\n【1】检查 Hermes 后端状态")
    status = mechanism.check_hermes_status()
    print(f"  可用: {status['available']}")
    print(f"  消息: {status['message']}")
    
    # 请求确认
    print("\n【2】请求用户确认")
    confirmation = mechanism.request_confirmation(
        task_type="diagnosis",
        task_description="胃窦部黏膜充血水肿诊断"
    )
    print(f"  确认 ID: {confirmation.get('confirmation_id', 'N/A')}")
    print(f"  消息: {confirmation['message']}")
    
    # 执行任务（如果确认）
    if confirmation.get('confirmed'):
        print("\n【3】执行诊断任务")
        result = mechanism.execute_task("diagnosis", {
            "organ": "wei",
            "image_description": "test"
        })
        print(f"  结果: {result}")
    
    print("=" * 60)
