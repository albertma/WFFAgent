from abc import abstractmethod
import json
import logging
import os
from typing import Any, Dict, List

from wff_agent import prompts

from wff_agent.utils import fin_reports_utils, stock_utils
from wff_agent.utils.stock_utils import is_valid_symbol
from wff_agent.agents.base_agent import AnalysisAgent
log = logging.getLogger(__name__)

class StockAnalysisAgent(AnalysisAgent):
    """股票分析 Agent 类"""
    
    def get_registered_tools(self) -> List[str]:
        """获取股票分析所需的工具列表
        
        Returns:
            List[str]: 工具名称列表
        """
        return [
            "GetMarketIndicators",
            "GetStockSentiment",
            "GetGlobalMarketIndicators",
        ]
    def prepare_input(self, input: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        log.info(f"StockAnalysisAgent 的输入: {input}")
        return input
    
    def get_output_file_name(self, input:Dict[str, Any]) -> str:
        return f"{input['symbol']}_{input['market']}_{self.__class__.__name__}.md"

    def after_ai_execute(self, result:str, input:Dict[str, Any]):
        """AI 执行后处理"""
        log.info(f"##########AI Agent {self.__class__.__name__} 执行后处理: {result}")
        output_file_name = self.get_output_file_name(input)
        file_path = "./reports/"
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        with open("./reports/" + output_file_name, "w") as f:
            f.write(result)
        
class FundamentalAnalysisAgent(StockAnalysisAgent):
    """基本面分析 Agent 类"""
    
    def prepare_input(self, input:Dict[str, Any], context:Dict[str, Any]) -> Dict[str, Any]:
        """准备输入"""
        symbol = input["symbol"]
        stock_info = stock_utils.get_latest_stock_price(symbol, input["market"])
        if input["market"] == "cn":
            input["stock_price"] = stock_info["最新"]
            input["total_shares"] = stock_info["总股本"]
        elif input["market"] == "us":
            input["stock_price"] = stock_info["price"]
        elif input["market"] == "hk":
            if input["total_shares"] is None:
                log.error("total_shares is None, hk market need total_shares")
                raise ValueError("total_shares is None, hk market need total_shares")
            log.debug(f"港股股票价格: {stock_info}")
            input["stock_price"] = stock_info["收盘"]
        
        input["fin_ratios"] = self.get_fin_ratios(symbol, input["market"], input["stock_price"], input["discount_rate"], input["growth_rate"], input["total_shares"])
        log.info("获取基本面数据完毕，准备执行基本面分析")
        return super().prepare_input(input, context)
    
    def get_fin_ratios(self, symbol:str, market:str, stock_price:float, discount_rate:float, growth_rate:float, total_shares:int) -> str:
        fin_ratios = fin_reports_utils.get_report_indicators(symbol, market, stock_price, discount_rate, growth_rate, total_shares)
        return fin_ratios
    
    def get_user_prompt(self, input:Dict[str, Any], context:Dict[str, Any]) -> str:
        """获取用户提示"""
        return prompts.FundamentalAnalysisPrompt
    
    def after_ai_execute(self, result:str, input:Dict[str, Any]):
        """AI 执行后处理"""
        super().after_ai_execute(result, input)
        input.remove("fin_ratios") ## make sure the input is not contain fin_ratios
        
    def get_system_prompt(self) -> str:
        return "你是一个专业的财务分析师，请分析公司的基本面, 并给出基本面分析报告(不要包含杜撰的数据)。"
class TechAnalysisAgent(StockAnalysisAgent):
    """技术分析 Agent 类，专门用于股票技术分析"""
        
    def get_user_prompt(self, input:Dict[str, Any], context:Dict[str, Any]) -> str:
        """获取用户提示"""
        log.info(f"技术分析 Agent 的输入: {input}")
        return prompts.TechnicalAnalysisPrompt
    
    def get_system_prompt(self) -> str:
        return "你是一个专业的技术分析师，请分析股票的技术指标, 并给出技术分析报告(不要包含杜撰的数据)。"

class NewsAnalysisAgent(StockAnalysisAgent):
    """新闻分析 Agent 类"""
    
    def get_user_prompt(self, input:Dict[str, Any], context:Dict[str, Any]) -> str:
        """获取用户提示"""
        log.info(f"新闻分析 Agent 的输入: {input}")
        return prompts.NewsAnalysisPrompt
    def get_system_prompt(self) -> str:
        return "你是一个专业的新闻分析师，请分析相关新闻, 并给出新闻分析报告(不要包含杜撰的数据)。"

class GlobalMarketAnalysisAgent(StockAnalysisAgent):
    """全球市场分析 Agent 类"""
    
    def get_user_prompt(self, input:Dict[str, Any], context:Dict[str, Any]) -> str:
        """获取用户提示"""
        log.info(f"全球市场分析 Agent 的输入: {input}")
        return prompts.GlobalMarketAnalysisPrompt
    
    def get_system_prompt(self) -> str:
        return "你是一个专业的全球市场分析师，请分析全球市场, 并给出全球市场分析报告(不要包含杜撰的数据)。"

class ComprehensiveAnalysisAgent(StockAnalysisAgent):
    """综合分析 Agent 类"""
    
    def get_user_prompt(self, input:Dict[str, Any], context:Dict[str, Any]) -> str:
        """获取用户提示"""
        return prompts.ComprehensiveAnalysisPrompt
    
    def get_system_prompt(self) -> str:
        return prompts.SystemStockAnalysisPrompt
    
    def prepare_input(self, input: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """准备输入"""
        if context["TechAnalysisAgent"]["output"] is None or len(context["TechAnalysisAgent"]["output"]) == 0:
            log.info(f"TechAnalysisAgent 的输出为空，读取文件: {input['symbol']}_{input['market']}_TechAnalysisAgent.md")
            input["technical_analysis"] = self.read_report_files(input, "TechAnalysisAgent")
        else:
            input["technical_analysis"] = context["TechAnalysisAgent"]["output"]
        
        if context["FundamentalAnalysisAgent"] is None or len(context["FundamentalAnalysisAgent"]["output"]) == 0:
            log.info(f"FundamentalAnalysisAgent 的输出为空，读取文件: {input['symbol']}_{input['market']}_FundamentalAnalysisAgent.md")
            input["fundamental_analysis"] = self.read_report_files(input, "FundamentalAnalysisAgent")
        else:
            input["fundamental_analysis"] = context["FundamentalAnalysisAgent"]["output"]
            
        if context["NewsAnalysisAgent"] is None or len(context["NewsAnalysisAgent"]["output"]) == 0:
            log.info(f"NewsAnalysisAgent 的输出为空，读取文件: {input['symbol']}_{input['market']}_NewsAnalysisAgent.md")
            input["news_analysis"] = self.read_report_files(input, "NewsAnalysisAgent")
        else:
            input["news_analysis"] = context["NewsAnalysisAgent"]["output"]
        if context["GlobalMarketAnalysisAgent"] is None or len(context["GlobalMarketAnalysisAgent"]["output"]) == 0:
            log.info(f"GlobalMarketAnalysisAgent 的输出为空，读取文件: {input['symbol']}_{input['market']}_GlobalMarketAnalysisAgent.md")
            input["global_market_analysis"] = self.read_report_files(input, "GlobalMarketAnalysisAgent")
        else:
            input["global_market_analysis"] = context["GlobalMarketAnalysisAgent"]["output"]
        return super().prepare_input(input, context)

    def read_report_files(self, input: Dict[str, Any], agent_name: str) -> str:
        file_path = f"./reports/{input['symbol']}_{input['market']}_{agent_name}.md"
        with open(file_path, "r") as f:
            return f.read()