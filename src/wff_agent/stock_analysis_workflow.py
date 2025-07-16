import asyncio
import logging
from typing import Dict, Any, List, Callable, Optional

from wff_agent import prompts
from wff_agent.agents.base_agent import AnalysisAgent
from wff_agent.workflows.base_workflow import Workflow, WorkflowStep
log = logging.getLogger(__name__)


class StockAnalysisWorkflow(Workflow):
    """股票分析工作流"""
    
    def __init__(self, agents: List[AnalysisAgent], progress_callback: Optional[Callable] = None):
        super().__init__(progress_callback=progress_callback)
        self.agents = agents
     
        
    def setup_steps(self):
        """设置工作流步骤"""
         # 基本面分析步骤
        for agent in self.agents:
            self.steps.append(WorkflowStep(
                name=agent.__class__.__name__,
                agent=agent,
                system_prompt=agent.get_system_prompt()
            ))
       
        
    def combine_results(self) -> Dict[str, Any]:
        """合并所有步骤的结果"""
        combined_report = {}
        for step in self.steps:
            combined_report[step.name] = step.result
        return combined_report
    
   