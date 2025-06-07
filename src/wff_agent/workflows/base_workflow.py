import logging
import os
from typing import Dict, Any, List
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
    
    def __init__(self):
        self.steps: List[WorkflowStep] = []
        self.results: Dict[str, Any] = {}
        self.context: Dict[str, Any] = {}
        
    @abstractmethod
    def setup_steps(self):
        """设置工作流步骤"""
        pass
    
    @abstractmethod
    def combine_results(self) -> Dict[str, Any]:
        """合并所有步骤的结果"""
        pass
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行工作流
        
        Args:
            input_data (Dict[str, Any]): 输入数据
            
        Returns:
            Dict[str, Any]: 工作流执行结果
        """
        log.info("开始执行工作流...")
        
        # 设置步骤
        self.setup_steps()
        
        # 执行每个步骤
        for step in self.steps:
            log.info(f"执行步骤: {step.name}")
            try:
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
                log.info(f"\n ##########步骤 {step.name} 执行完成")
                log.info(f"\n ##########步骤 {step.name} 的输出: {result}")
                # write result to markdown file
                output_file_name = step.agent.get_output_file_name(input_data)
                file_path = "./reports/"
                if not os.path.exists(file_path):
                    os.makedirs(file_path)
                with open("./reports/"+output_file_name, "w") as f:
                    f.write(result)
            except Exception as e:
                log.error(f"##########步骤 {step.name} 执行失败: {str(e)}", exc_info=True)
            finally:
                if step.result is None:
                    log.error(f"##########步骤 {step.name} 执行失败, 结果设置为 ERROR")
                    self.context[step.name] = {
                        "output": "ERROR"
                    }
                    self.results[step.name] = "ERROR"
        
        # 合并结果
        final_result = self.combine_results()
        log.info("工作流执行完成")
        
        return final_result 