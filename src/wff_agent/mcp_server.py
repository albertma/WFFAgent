# -*- coding: utf-8 -*-
import asyncio
from mcp.server.fastmcp import FastMCP

from wff_agent.utils import macro_utils
from wff_agent.utils import fin_reports_utils, stock_utils
from typing import Dict, Any, List
import logging
import os
from wff_agent.datasource import akshare_request as ak_request 
from wff_agent.datasource import alpha_v_request as av_request

# 设置更详细的日志格式
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
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
            price = av_request.get_us_stock_info(symbol)
        elif market == 'cn':
            price = ak_request.get_cn_stock_info(symbol)["最新"]
        elif market == 'hk':
            price = ak_request.get_hk_stock_info(symbol)
        log.debug(f"获取到的股票价格: {price}")
        return price
    except Exception as e:
        log.error(f"获取股票价格失败: {str(e)}", exc_info=True)
        raise

@mcp.tool(name="GetStockSentiment")
async def GetStockSentiment(symbol:str, market:str) -> List[Dict[str, Any]]:
    """获取股票情绪
    Args:
        symbol (str): 股票代码
        market (str): 市场, us, cn, hk
    Returns:
        Dict[str, Any]: 股票情绪
    """
    try:
        log.info(f"开始获取股票情绪: {symbol}, {market}")
        result = stock_utils.get_stock_sentiment(symbol, market)
        log.info(f"获取到的股票情绪: {result}")
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
        log.info(f"\n ##########开始获取全球市场指标")
        result = stock_utils.get_global_market_indicators()
        log.info(f"获取到的全球市场指标: {result}")
        return result
    except Exception as e:
        log.error(f"获取全球市场指标失败: {str(e)}", exc_info=True)
        raise e
#@mcp.tool(name="GetMacroData")
# async def GetMacroData(symbol:str, market:str) -> Dict[str, Any]:
#     """获取宏观数据
#     Returns:
#         Dict[str, Any]: 宏观数据
#     """
#     try:
#         log.info(f"开始获取宏观数据: {symbol}, {market}")
#         result = macro_utils.get_macro_data()
#         log.debug(f"获取到的宏观数据: {result}")
#         return result
#     except Exception as e:
#         log.error(f"获取宏观数据失败: {str(e)}", exc_info=True)
#         raise e
    
#@mcp.tool(name="AnalyzeFinancialReport")
# async def AnalyzeFinancialReport(symbol:str, market:str, stock_price:float, 
#                              discount_rate:float=0.06, growth_rate:float=0.02, total_shares:int=1) -> Dict[str, Any]:
    # """
    # 分析财务指标
    # Args:
    #     symbol (str): 股票代码
    #     market (str): 市场, us, cn, hk
    #     stock_price (float): 股票价格
    #     discount_rate (float): 折现率
    #     total_shares (int): 总股本
    # """
        # try:
        #     log.info(f"\n ##########开始分析财务指标: {symbol}, {market}, {stock_price}, {discount_rate}, {growth_rate}, {total_shares}")
        #     fin_indicators = fin_reports_utils.get_report_indicators(symbol, market, stock_price, discount_rate, growth_rate, total_shares)
        #     log.info(f"\n ##########分析得到的财务指标: {fin_indicators}")
        #     return fin_indicators
        # except Exception as e:
        #     log.error(f"分析财务指标失败: {str(e)}", exc_info=True)
        #     raise

if __name__ == "__main__":
    log.info("启动 MCP 服务器")
    try:
        mcp.run()
    except KeyboardInterrupt:
        log.info("服务器被用户中断")
    except Exception as e:
        log.error(f"服务器发生错误: {e}")
    finally:
        log.info("服务器关闭")
        # 确保所有连接都被正确关闭        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.stop()
            loop.close()
        except Exception as e:
            log.error(f"关闭事件循环时发生错误: {e}")
        exit(0)
   
   
    