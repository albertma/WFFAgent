# server.py
from mcp.server.fastmcp import FastMCP

import financial_indicators as fi
from typing import Dict, Any
import logging
import asyncio
import os
import stock_client
import agent_utils

logging.basicConfig(level=logging.DEBUG)
mcp = FastMCP("FinancialAnalyst")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

@mcp.tool()
async def get_current_stockprice(symbol: str) -> Dict[str, Any]:
    """获取当前股价"""
    stock_price = stock_client.get_stock_price_vantage(symbol=symbol)
    print(f"获取到的当前股价: {stock_price}")
    return {"currentPrice": stock_price}

@mcp.tool()
async def analyze_financials(symbol:str, stock_price:float, 
                             discount_rate:float=0.06, growth_rate:float=0.02) -> Dict[str, Any]:
    """财务关键指标计算"""
    # 将dictionary string转换为字典
    balance_sheet = agent_utils.read_json(r"./AAPL&BALANCE_SHEET.json")
    income_statement = agent_utils.read_json(r"./AAPL&INCOME_STATEMENT.json")
    cashflow = agent_utils.read_json(r"./AAPL&CASH_FLOW.json")
    reports =  {
        "balanceSheet": balance_sheet, 
        "incomeStatement": income_statement,
        "cashflow": cashflow
        } 
    if stock_price is None or reports is None:
        return {"error": f"""param stock_price:{stock_price}, reports:{reports}"""}
    logging.debug(f"股票价格：{stock_price}, 开始计算财务指标")
    try:
        indictors = fi.calculate_financial_indicators(reports, stock_price, discount_rate=discount_rate, growth_rate=growth_rate)  
        logging.debug(f"计算出的财务指标: {indictors}")
        return indictors
    except Exception as e:
        logging.debug(f"计算财务指标时发生错误: {e}")
        return {"error": str(e)}
    

@mcp.tool()  
async def get_management_discussion(symbol:str) -> str:
    """获取管理层讨论"""
    # read aapl_memo.txt
    name = f"{symbol}_MEMO.txt"
    discussion = agent_utils.read_file(name)
    logging.debug(f"discussion:{discussion}") 
    return discussion

async def main():
    # 运行FastMCP
    content = await get_management_discussion("AAPL")
    print(f"计算出的财务指标: {content}")
    
if __name__ == "__main__":
    # 运行FastMCP
    mcp.run()
    #asyncio.run(main())
   
   
    