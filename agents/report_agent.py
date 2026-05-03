"""
AIMED Report Agent - 报告生成智能体

负责：
- 结构化报告生成
- 多语言支持（中/英/法/日/韩/俄）
- PDF 导出
- 模板管理
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
import os

from .base_agent import SupportAgent, AgentMessage

from .base_agent import SupportAgent, AgentMessage


class ReportAgent(SupportAgent):
    """
    报告生成 Agent - 生成结构化诊断报告
    继承 SupportAgent 基类
    """
    
    def __init__(self):
        config = {
            'agent_name': 'Report Agent',
            'agent_version': '2.0.0',
            'description': '报告生成 Agent - 生成结构化诊断报告'
        }
        super().__init__(agent_id="report", config=config)
        self.template_dir = "templates"
        self.output_dir = "data/reports"
        self.supported_languages = ["zh", "en", "fr", "ja", "ko", "ru"]
        self.report_count = 0
        logger.info("ReportAgent 初始化完成 (V2.0 架构)")
    
    def generate_report(self, 
                       patient_info: Dict[str, Any],
                       diagnosis_results: List[Dict[str, Any]],
                       doctor_info: Dict[str, str],
                       language: str = "zh") -> Dict[str, Any]:
        """
        生成诊断报告
        
        Args:
            patient_info: 患者信息 {patient_id, name, gender, age}
            diagnosis_results: 诊断结果列表
            doctor_info: 医生信息 {doctor_id, name}
            language: 报告语言（默认中文）
        
        Returns:
            报告生成结果
        """
        self.report_count += 1
        report_id = f"RPT_{datetime.now().strftime('%Y%m%d%H%M%S')}_{self.report_count}"
        
        logger.info(f"生成报告：{report_id}, 语言：{language}")
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 构建报告内容
        report_content = {
            "report_id": report_id,
            "generated_at": datetime.now().isoformat(),
            "language": language,
            "patient_info": patient_info,
            "doctor_info": doctor_info,
            "diagnosis_results": diagnosis_results,
            "disclaimer": self._get_disclaimer(language)
        }
        
        # TODO: 根据模板生成 PDF
        pdf_path = f"{self.output_dir}/{report_id}.pdf"
        
        logger.info(f"报告生成完成：{report_id}, PDF 路径：{pdf_path}")
        
        return {
            "report_id": report_id,
            "status": "success",
            "pdf_path": pdf_path,
            "content": report_content
        }
    
    def _get_disclaimer(self, language: str) -> str:
        """
        获取多语言免责声明
        """
        disclaimers = {
            "zh": "免责声明：本报告由 AI 辅助生成，仅供医生参考，最终诊断请以执业医师判断为准。",
            "en": "Disclaimer: This report is AI-assisted and for physician reference only. Final diagnosis shall be made by licensed physicians.",
            "fr": "Avis de non-responsabilité: Ce rapport est assisté par IA et à titre de référence uniquement. Le diagnostic final doit être établi par un médecin agréé.",
            "ja": "免責事項：このレポートは AI 支援によるもので、医師の参考用です。最終診断は免許を持つ医師によって行われます。",
            "ko": "면책 조항: 이 보고서는 AI 보조이며 의사 참조용입니다. 최종 진단은 면허 있는 의사가 내립니다.",
            "ru": "Отказ от ответственности: Этот отчет создан с помощью ИИ и предназначен только для справки. Окончательный диагноз должен быть поставлен лицензированным врачом."
        }
        
        return disclaimers.get(language, disclaimers["zh"])
    
    def get_template(self, template_name: str, language: str = "zh") -> Optional[str]:
        """
        获取报告模板
        """
        template_path = f"{self.template_dir}/{template_name}_{language}.md"
        
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        logger.warning(f"模板不存在：{template_path}")
        return None
    
    def export_pdf(self, report_content: Dict[str, Any], output_path: str) -> bool:
        """
        导出 PDF 报告
        """
        logger.info(f"导出 PDF: {output_path}")
        
        # TODO: 实际 PDF 生成逻辑
        # 使用 reportlab 或其他 PDF 库
        
        return True
    
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
            if message.message_type == 'generate_report':
                # 生成报告
                patient_info = payload.get('patient_info', {})
                diagnosis_results = payload.get('diagnosis_results', [])
                doctor_info = payload.get('doctor_info', {})
                language = payload.get('language', 'zh')
                
                result = self.generate_report(patient_info, diagnosis_results, doctor_info, language)
                
                return AgentMessage(
                    sender_id=self.agent_id,
                    receiver_id=message.sender_id,
                    message_type='report_result',
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
            logger.error(f"ReportAgent 处理消息失败：{e}")
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
        return ['report_generation', 'multi_language_support', 'pdf_export', 'template_management']
    
    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行支撑任务（实现 SupportAgent 抽象方法）
        """
        task_type = task_data.get('task_type', 'generate_report')
        
        if task_type == 'generate_report':
            return self.generate_report(
                task_data.get('patient_info', {}),
                task_data.get('diagnosis_results', []),
                task_data.get('doctor_info', {}),
                task_data.get('language', 'zh')
            )
        else:
            return {'error': f'未知任务类型：{task_type}'}
    
    def get_statistics(self) -> Dict:
        """
        获取统计信息
        """
        return {
            "total_reports": self.report_count,
            "supported_languages": self.supported_languages,
            "template_dir": self.template_dir,
            "output_dir": self.output_dir,
            "agent_id": self.agent_id,
            "agent_version": self.config.get('agent_version', '2.0.0')
        }

# 单例实例
report_agent = ReportAgent()
