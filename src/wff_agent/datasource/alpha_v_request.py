# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
import logging
import os
import requests
from wff_agent.datasource import file_lru_cache as filecache

log = logging.getLogger(__name__)


ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")


def _get_fin_report(symbol: str, report_type: str = "BALANCE_SHEET") -> dict:
    
    url = f'https://www.alphavantage.co/query?function={report_type}&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}'
    r = requests.get(url)
    data = r.json()
    return data

@filecache.cached("us_stock_info", expire_seconds=60*60*4)
def get_us_stock_info(symbol: str) -> float:
    """获取美股股票价格
    """
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}'
    r = requests.get(url)
    data = r.json()
    print(data)
    try:
        return {
            "symbol": symbol,
            "price": float(data["Global Quote"]["05. price"]),
            "market": "us"
        }
    except KeyError:
        log.error(f"请求失败：请检查API密钥或股票代码{symbol}")
        raise Exception(f"请求失败：请检查API密钥或股票代码{symbol}")
    

@filecache.cached("us_stock_financial_report", expire_seconds=60*60*24*30)
def get_stock_financial_report_us(symbol: str) -> dict:
    """获取财务报表

    Args:
        symbol (str): 股票代码

    Returns:
        dict: 财务报表
    """
    try:
        balance_sheet = None
        income_statement = None
        cash_flow = None
        with ThreadPoolExecutor(max_workers=10) as executor:
            balance_sheet_future = executor.submit(_get_fin_report, symbol, "BALANCE_SHEET")
            income_statement_future = executor.submit(_get_fin_report, symbol, "INCOME_STATEMENT")
            cash_flow_future = executor.submit(_get_fin_report, symbol, "CASH_FLOW")

            balance_sheet = balance_sheet_future.result()
            income_statement = income_statement_future.result()
            cash_flow = cash_flow_future.result() 
            if balance_sheet is None or len(balance_sheet) == 0:
                log.error(f"获取 {symbol} 资产负债表失败")
                raise Exception(f"获取 {symbol} 资产负债表失败")
            if income_statement is None or len(income_statement) == 0:
                log.error(f"获取 {symbol} 利润表失败")
                raise Exception(f"获取 {symbol} 利润表失败")
            if cash_flow is None or len(cash_flow) == 0:
                log.error(f"获取 {symbol} 现金流量表失败")
                raise Exception(f"获取 {symbol} 现金流量表失败")
    except Exception as e:
        log.error(f"获取 {symbol} 财务报表失败: {e}")
        raise Exception(f"获取 {symbol} 财务报表失败: {e}")
    
    return {
        "balance_sheet": balance_sheet,
        "income_statement": income_statement,
        "cashflow": cash_flow
    }


if __name__ == "__main__":
    data = get_us_stock_info("AAPL")
    print(data)
