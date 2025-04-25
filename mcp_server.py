# server.py
from mcp.server.fastmcp import FastMCP

import json
import financial_indicators as fi
from typing import Dict, Any
import logging
import asyncio

logging.basicConfig(level=logging.DEBUG)
mcp = FastMCP("FinancialAnalyst")

def _readjson(file_path)-> dict:
    """读取JSON文件"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data        
    except FileNotFoundError:
        print(f"文件路径错误：{file_path} 不存在")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON格式错误：第{e.lineno}行，错误原因：{e.msg}")
        return None

@mcp.tool()
async def get_current_stockprice(symbol: str) -> Dict[str, Any]:
    """获取当前股价"""
    # 这里可以使用yfinance等库获取实时股价
    # 例如：stock_price = yfinance.Ticker(symbol).info['currentPrice']
    stock_price = 199.00  # 假设当前股价为175美元
    print(f"获取到的当前股价: {stock_price}")
    return {"currentPrice": stock_price}

@mcp.tool()
async def analyze_financials(symbol:str, stock_price:float) -> Dict[str, Any]:
    """财务关键指标计算"""
    # 将dictionary string转换为字典
    balance_sheet = _readjson(r"./AAPL&BALANCE_SHEET.json")
    income_statement = _readjson(r"./AAPL&INCOME_STATEMENT.json")
    cashflow = _readjson(r"./AAPL&CASH_FLOW.json")
    reports =  {
        "balanceSheet": balance_sheet, 
        "incomeStatement": income_statement,
        "cashflow": cashflow
        } 
    if stock_price is None or reports is None:
        return {"error": f"""param stock_price:{stock_price}, reports:{reports}"""}
    logging.debug("开始计算财务指标")
    try:
        indictors = fi.calculate_financial_indicators(reports, stock_price)  
        logging.debug(f"计算出的财务指标: {indictors}")
        return indictors
    except Exception as e:
        logging.debug(f"计算财务指标时发生错误: {e}")
        return {"error": str(e)}
    

@mcp.tool()  
async def get_management_discussion(symbol:str) -> str:
    """获取管理层讨论"""
    # read appl_memo.txt
    with open("appl_memo.txt", "r", encoding="utf-8") as file:
        content = file.read()
        print(f"获取到的管理层讨论: {content}")
        return content

async def main():
    # 运行FastMCP
    
    content = await get_management_discussion("AAPL")
    print(f"计算出的财务指标: {content}")
    
if __name__ == "__main__":
    # 运行FastMCP
    mcp.run()
    #asyncio.run(main())
   
   
    