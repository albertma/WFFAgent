import asyncio
import logging
from typing import Dict, Any, List

from wff_agent import prompts
from wff_agent.agents.base_agent import AnalysisAgent
from wff_agent.workflows.base_workflow import Workflow, WorkflowStep
log = logging.getLogger(__name__)


    

class StockAnalysisWorkflow(Workflow):
    """股票分析工作流"""
    
    def __init__(self, technical_agent: AnalysisAgent, 
                 fundamental_agent: AnalysisAgent, 
                 news_agent: AnalysisAgent, 
                 comprehensive_agent: AnalysisAgent):
        super().__init__()
        self.technical_agent = technical_agent
        self.fundamental_agent = fundamental_agent
        self.news_agent = news_agent
        self.comprehensive_agent = comprehensive_agent
        
    def setup_steps(self):
        """设置工作流步骤"""
         # 基本面分析步骤
        self.steps.append(WorkflowStep(
            name="fundamental_analysis",
            agent=self.fundamental_agent,
            system_prompt="你是一个专业的财务分析师，请分析公司的基本面。"
        ))
        
        # 技术分析步骤
        self.steps.append(WorkflowStep(
            name="technical_analysis",
            agent=self.technical_agent,
            system_prompt="你是一个专业的技术分析师，请分析股票的技术指标。"
        ))
        
        # 新闻分析步骤
        self.steps.append(WorkflowStep(
            name="news_analysis",
            agent=self.news_agent,
            system_prompt="你是一个专业的新闻分析师，请分析相关新闻。"
        ))
        
        self.steps.append(WorkflowStep(
            name="comprehensive_analysis",
            agent=self.comprehensive_agent,
            system_prompt=prompts.SystemStockAnalysisPrompt
        ))
    
    def combine_results(self) -> Dict[str, Any]:
        """合并所有步骤的结果"""
        combined_report = {
            "technical_analysis": self.results["technical_analysis"],
            "fundamental_analysis": self.results["fundamental_analysis"],
            "news_analysis": self.results["news_analysis"],
            "comprehensive_analysis": self.results["comprehensive_analysis"]
        }
        return combined_report
    
   