from abc import abstractmethod
import logging
from typing import Any, Dict, List

from . import prompts

from .utils import stock_utils
from .utils.stock_utils import is_valid_symbol
from .agents.base_agent import AnalysisAgent
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
            "AnalyzeFinancials",     
        ]
    def prepare_input(self, input: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return input
    
    def get_output_file_name(self, input:Dict[str, Any]) -> str:
        return f"{input['symbol']}_{input['market']}_{self.__class__.__name__}.md"

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
        return super().prepare_input(input, context)
    
    def get_user_prompt(self, input:Dict[str, Any], context:Dict[str, Any]) -> str:
        """获取用户提示"""
        return prompts.FundamentalAnalysisPrompt
    
class TechAnalysisAgent(StockAnalysisAgent):
    """技术分析 Agent 类，专门用于股票技术分析"""
        
    def get_user_prompt(self, input:Dict[str, Any], context:Dict[str, Any]) -> str:
        """获取用户提示"""
        log.info(f"技术分析 Agent 的输入: {input}")
        return prompts.TechnicalAnalysisPrompt


class NewsAnalysisAgent(StockAnalysisAgent):
    """新闻分析 Agent 类"""
    
    def get_user_prompt(self, input:Dict[str, Any], context:Dict[str, Any]) -> str:
        """获取用户提示"""
        log.info(f"新闻分析 Agent 的输入: {input}")
        return prompts.NewsAnalysisPrompt
    
class ComprehensiveAnalysisAgent(StockAnalysisAgent):
    """综合分析 Agent 类"""
    
    def get_user_prompt(self, input:Dict[str, Any], context:Dict[str, Any]) -> str:
        """获取用户提示"""
        return prompts.ComprehensiveAnalysisPrompt
    
    def prepare_input(self, input: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """准备输入"""
        input["technical_analysis"] = context["technical_analysis"]
        input["fundamental_analysis"] = context["fundamental_analysis"]
        input["news_analysis"] = context["news_analysis"]
        return super().prepare_input(input, context)
