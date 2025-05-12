# server.py
from mcp.server.fastmcp import FastMCP

from .utils import macro_utils
from .utils import fin_reports_utils,stock_utils, agent_utils
from typing import Dict, Any, List
import logging
import os
from .datasource import akshare_utils as akutils 
from .datasource import alpha_v_utils as alpha_v_utils

# 设置更详细的日志格式
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

mcp = FastMCP("FinancialAnalyst")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

@mcp.tool(name="GetMarketIndicators")
async def GetMarketIndicators(symbol: str, market:str, windows:int=50) -> Dict[str, Any]:
    """Get stock market indicators

    Args:
        symbol (str): stock symbol
        market (str): market, us, cn, hk
        windows (int): data windows, default 50
    Returns:
        Dict[str, Any]: stock market indicators
    """
    try:
        log.info(f"开始获取股票技术指标: {symbol}, {market}")
        result = stock_utils.get_market_indicators(symbol, market)
        log.debug(f"获取到的技术指标数据: {result}")
        return result
    except Exception as e:
        log.error(f"获取技术指标失败: {str(e)}", exc_info=True)
        raise

@mcp.tool(name="GetLatestStockPrice")
async def GetLatestStockPrice(symbol:str, market:str) -> List[Dict[str,Any]]:
    """获取最新股票价格

    Args:
        symbol (str): 股票代码
        market (str): 市场, us, cn, hk

    Returns:
        float: 股票价格
    """
    try:
        log.info(f"开始获取最新股票价格: {symbol}, {market}")
        price = None
        if market == 'us':
            price = alpha_v_utils.get_us_stock_price(symbol)
        elif market == 'cn':
            price = akutils.get_stock_info(symbol)["最新价"]
        elif market == 'hk':
            price = akutils.get_stock_price_hk(symbol)
        log.debug(f"获取到的股票价格: {price}")
        return price
    except Exception as e:
        log.error(f"获取股票价格失败: {str(e)}", exc_info=True)
        raise

@mcp.tool(name="GetSentiment")
async def GetSentiment(symbol:str, market:str) -> Dict[str, Any]:
    """获取股票情绪
    Args:
        symbol (str): 股票代码
        market (str): 市场, us, cn, hk
    Returns:
        Dict[str, Any]: 股票情绪
    """
    try:
        log.info(f"开始获取股票情绪: {symbol}, {market}")
        result = stock_utils.get_sentiment(symbol, market)
        log.debug(f"获取到的股票情绪: {result}")
        return result
    except Exception as e:
        log.error(f"获取股票情绪失败: {str(e)}", exc_info=True)
        raise e
    
@mcp.tool(name="GetGlobalMarketIndicators")
async def GetGlobalMarketIndicators() -> Dict[str, Any]:
    """获取全球市场指标
    Returns:
        Dict[str, Any]: 全球市场指标
    """
    try:
        log.info(f"开始获取全球市场指标")
        result = stock_utils.get_global_market_indicators()
        log.debug(f"获取到的全球市场指标: {result}")
        return result
    except Exception as e:
        log.error(f"获取全球市场指标失败: {str(e)}", exc_info=True)
        raise e
@mcp.tool(name="GetMacroData")
async def GetMacroData(symbol:str, market:str) -> Dict[str, Any]:
    """获取宏观数据
    Returns:
        Dict[str, Any]: 宏观数据
    """
    try:
        log.info(f"开始获取宏观数据: {symbol}, {market}")
        result = macro_utils.get_macro_data(symbol, market)
        log.debug(f"获取到的宏观数据: {result}")
        return result
    except Exception as e:
        log.error(f"获取宏观数据失败: {str(e)}", exc_info=True)
        raise e
    
@mcp.tool(name="AnalyzeFinancials")
async def AnalyzeFinancials(symbol:str, market:str, stock_price:float, 
                             discount_rate:float=0.06, growth_rate:float=0.02, total_shares:int=1) -> Dict[str, Any]:
    """
    分析财务指标
    Args:
        symbol (str): 股票代码
        market (str): 市场, us, cn, hk
        stock_price (float): 股票价格
        discount_rate (float): 折现率
        total_shares (int): 总股本
    """
    try:
        log.info(f"开始分析财务指标: {symbol}, {market}, {stock_price}, {discount_rate}, {growth_rate}, {total_shares}")
        fin_indicators = fin_reports_utils.get_report_indicators(symbol, market, stock_price, discount_rate, growth_rate, total_shares)
        log.debug(f"分析得到的财务指标: {fin_indicators}")
        return fin_indicators
    except Exception as e:
        log.error(f"分析财务指标失败: {str(e)}", exc_info=True)
        raise


# @mcp.tool(name="CheckValidSymbol")
# async def CheckValidSymbol(symbol:str, market:str) -> bool:
    
#     try:
#         log.info(f"开始检查股票代码有效性: {symbol}, {market}")
#         result = False
#         if market.lower() == 'us':
#             if symbol.isalpha():
#                 result = akutils.is_valid_us_stock_symbols(symbol=symbol)
#         elif market.lower() == 'cn':
#             result = symbol.isdigit() and len(symbol) == 6
#         elif market.lower() == 'hk':
#             result = symbol.isdigit() and len(symbol) == 5
#         else:
#             raise ValueError("Invalid market")
#         log.debug(f"股票代码有效性检查结果: {result}")
#         return result
#     except Exception as e:
#         log.error(f"检查股票代码有效性失败: {str(e)}", exc_info=True)
#         raise

# async def main():
#     """主函数用于测试"""
#     try:
#         log.info("开始测试管理层讨论获取功能")
#         content = await GetManagementDiscussion("AAPL", "us")
#         log.info(f"获取到的管理层讨论内容: {content}")
#     except Exception as e:
#         log.error(f"测试失败: {str(e)}", exc_info=True)

if __name__ == "__main__":
    log.info("启动 MCP 服务器")
    mcp.run()
    #asyncio.run(main())
   
   
    