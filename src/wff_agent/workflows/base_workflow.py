import logging
import os
from typing import Dict, Any, List, Callable, Optional
from abc import ABC, abstractmethod

from wff_agent.agents.base_agent import AnalysisAgent

log = logging.getLogger(__name__)

class WorkflowStep:
    """工作流步骤"""
    def __init__(self, name: str, agent: AnalysisAgent, system_prompt: str):
        self.name = name
        self.agent = agent
        self.system_prompt = system_prompt
        self.result = None

class Workflow(ABC):
    """工作流基类"""
    
    def __init__(self, progress_callback: Optional[Callable] = None):
        self.steps: List[WorkflowStep] = []
        self.results: Dict[str, Any] = {}
        self.context: Dict[str, Any] = {}
        self.progress_callback = progress_callback
        
    @abstractmethod
    def setup_steps(self):
        """设置工作流步骤"""
        pass
    
    @abstractmethod
    def combine_results(self) -> Dict[str, Any]:
        """合并所有步骤的结果"""
        pass
    
    def update_progress(self, step_name: str, result: str, status: str = "completed"):
        """更新进度回调"""
        if self.progress_callback:
            try:
                self.progress_callback(step_name, result, status)
            except Exception as e:
                log.error(f"进度回调执行失败: {e}")
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行工作流
        
        Args:
            input_data (Dict[str, Any]): 输入数据
            
        Returns:
            Dict[str, Any]: 工作流执行结果
        """
        
        # 设置步骤
        self.setup_steps()
        
        # 执行每个步骤
        for step in self.steps:
            log.info(f"\n ##########开始执行步骤: {step.name}...")
            try:
                # 通知开始执行步骤
                self.update_progress(step.name, f"开始执行 {step.name}...", "started")
                
                input_data = step.agent.prepare_input(input_data, self.context)
                user_prompt = step.agent.get_user_prompt(input_data, self.context)
                log.info(f"\n ##########执行步骤: {step.name} 的输入数据: {input_data}")
                result = await step.agent.execute_with_session(
                    system_prompt=step.system_prompt,
                    user_message_prompt=user_prompt,
                    input=input_data
                )
                
                self.context[step.name] = {
                    "output": result
                }
                step.result = result
                self.results[step.name] = result
                log.info(f"\n ##########步骤 {step.name} 执行完成, 输出: {result}")
                step.agent.after_ai_execute(result, input_data)
                
                # 通知步骤完成
                self.update_progress(step.name, result, "completed")
                
            except Exception as e:
                log.error(f"##########步骤 {step.name} 执行失败: {str(e)}", exc_info=True)
                # 通知步骤失败
                self.update_progress(step.name, f"执行失败: {str(e)}", "failed")
            finally:
                if step.result is None:
                    log.error(f"##########步骤 {step.name} 执行失败, 结果设置为 ERROR")
                    self.context[step.name] = {
                        "output": "ERROR"
                    }
                    self.results[step.name] = "ERROR"
                    # 通知步骤失败
                    self.update_progress(step.name, "ERROR", "failed")
        
        # 合并结果
        final_result = self.combine_results()
        log.info("工作流执行完成")
        
        return final_result 