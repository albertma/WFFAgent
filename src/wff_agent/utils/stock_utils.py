# -*- coding: utf-8 -*-
import logging
import pandas as pd
from typing import Any, Dict, List

from wff_agent.datasource import akshare_request as ak_request, news_request
from wff_agent.datasource import alpha_v_request as av_request
from wff_agent.datasource import file_lru_cache as lru_cache
log = logging.getLogger(__name__)

def get_market_indicators(symbol: str, market: str, windows_size:int=50) -> Dict[str, Any]:
    """
    获取市场指标
    """
    log.info(f"开始获取市场指标: {symbol}, {market}")
    df = ak_request.get_stock_history(symbol, market)
    if df is None:
        log.error(f"获取历史数据失败: {symbol}")
        return {"error": f"""param history is None"""}
    # 计算市场指标
    df.sort_values(by="日期", inplace=True, ascending=True)
    if df is None:
        log.error(f"获取历史数据失败: {symbol}")
        return {"error": f"""param history is None"""}
    # 计算市场指标
    df["MA5"] = df["收盘"].rolling(window=5).mean()
    df["MA20"] = df["收盘"].rolling(window=20).mean()
    df["MA60"] = df["收盘"].rolling(window=60).mean()
    df["MA50"] = df["收盘"].rolling(window=120).mean() #50日均线，牛熊指标 
    df["MA200"] = df["收盘"].rolling(window=240).mean()#200日均线, 牛熊指标
    #计算EMA
    df["EMA9"] = df["收盘"].ewm(span=9, adjust=False).mean()
    df["EMA12"] = df["收盘"].ewm(span=12, adjust=False).mean()
    df["EMA21"] = df["收盘"].ewm(span=21, adjust=False).mean()
    df["EMA26"] = df["收盘"].ewm(span=26, adjust=False).mean()
    df["EMA50"] = df["收盘"].ewm(span=50, adjust=False).mean()

    
    #计算MACD
    df["DIF"] = df["EMA12"] - df["EMA26"] #快线
    df["DEA"] = df["DIF"].ewm(span=9, adjust=False).mean() #慢线
    df["MACD"] = 2 * (df["DIF"] - df["DEA"]) #柱状图
    #计算KDJ
    df["RSV"] = (df["收盘"] - df["最低"].rolling(window=9).min()) / (df["最高"].rolling(window=9).max() - df["最低"].rolling(window=9).min()) * 100
    df["K"] = df["RSV"].ewm(span=3, adjust=False).mean()
    df["D"] = df["K"].ewm(span=3, adjust=False).mean()
    df["J"] = 3 * df["K"] - 2 * df["D"]
    #计算RSI
    # 计算价格变化
    delta = df["收盘"].diff()
    # 分别获取上涨和下跌
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    # 计算相对强度
    rs = gain / loss
    # 计算RSI
    df["RSI"] = 100 - (100 / (1 + rs))
    #计算BOLL
    df["BOLL"] = df["收盘"].rolling(window=20).mean()
    df["BOLL_UP"] = df["BOLL"] + 2 * df["收盘"].rolling(window=20).std()
    df["BOLL_DOWN"] = df["BOLL"] - 2 * df["收盘"].rolling(window=20).std()
    #计算OBV
    df["OBV"] = (df["成交量"].where(df["收盘"].diff() > 0, 0).rolling(window=20).sum() - df["成交量"].where(df["收盘"].diff() < 0, 0).rolling(window=20).sum()) / df["成交量"].rolling(window=20).sum()
    # 只保留需要的列, 把日期作为索引
    df = df[['收盘', '成交量', 'MA5', 'MA20', 'MA60','MA200', 
             'EMA9', 'EMA12', 'K','D','J', 
             'RSI',  'DIF', 'DEA', 'MACD', 'BOLL', 'BOLL_UP', 'BOLL_DOWN', 'OBV']].tail(windows_size)
    
    # 重置索引，将日期作为列
    df = df.reset_index()
    # 将日期转换成字符串
    df["日期"] = df["日期"].astype(str)
    # 转换为JSON，每个对象包含日期属性
    json_data = df.to_json(force_ascii=False, orient="records")
    log.info(f"获取市场指标: {symbol}, {market}, {windows_size}, {json_data}")
    return json_data

def get_global_market_indicators() -> Dict[str, Any]:
    """
    获取全球市场指标
    """
    log.info(f"开始获取全球市场指标")
    df = ak_request.get_global_index()
    if df is None:
        log.error(f"获取全球指数失败")
        return {"error": f"""param global_index is None"""}
    # 只保留需要的列, 把日期作为索引
    df = df[['代码', '名称', '最新价', '涨跌幅', '涨跌额',   '振幅', '开盘价', '最高价', '最低价', '昨收价']]
    return df.to_json(force_ascii=False, orient="records")  

def get_latest_stock_price(symbol: str, market: str) -> Dict[str, Any]:
    """
    获取最新股票价格
    """
    log.info(f"开始获取最新股票价格: {symbol}, {market}")
    if market == "cn":
        return ak_request.get_cn_stock_info(symbol)
    elif market == "us":
        return av_request.get_us_stock_info(symbol)
    elif market == "hk":
        value = ak_request.get_hk_stock_info(symbol)
        return value
    else:
        return 0
    
def is_valid_symbol(symbol: str, market: str) -> bool:
    """
    检查股票代码是否有效
    """
    if market == "cn":
        # check symbol is 6 digits
        return len(symbol) == 6 and symbol.isdigit()
    elif market == "us":
        return symbol.isalpha()
    elif market == "hk":
        return symbol.isdigit() and len(symbol) == 5
    return False

def _get_cn_stock_news(symbol: str) -> List[Dict[str, Any]]:
    """
    获取东方财富网的新闻
    
    Args:
        symbol (str): 股票代码
        
    Returns:
        List[Dict[str, Any]]: 新闻列表，每个新闻包含标题、来源、链接和内容
    """
    try:
        # 获取新闻数据
        df = ak_request.get_cn_news_from_eastmoney(symbol).head(20) # 获取最新的5条新闻
        news_list = []
        
        for index, row in df.iterrows():
            news = {
                "title": row["新闻标题"],
                "source": row["文章来源"],
                "link": row["新闻链接"],
                "content": row["新闻内容"],
                "date": row["发布时间"]
            }
            news_list.append(news)
        return news_list
        
    except Exception as e:
        log.error(f"获取新闻列表失败: {str(e)}")
        return []
def _get_us_hk_stock_news(symbol: str, market: str) -> List[Dict[str, Any]]:
    """
    获取美国股票新闻
    """
    log.info(f"开始获取美国/香港股票新闻: {symbol}")
    if market == "us":
        keyword = "美股:" + symbol
    elif market == "hk":
        keyword = "港股:" + symbol
    else:
        raise ValueError(f"Invalid market: {market}")
    news = news_request.get_news_from_newapi([keyword], 10)
    return news

def _get_global_financial_news() -> List[Dict[str, Any]]:
    """
    获取全球股票新闻
    """
    log.info(f"开始获取全球股票新闻")
    df = ak_request.get_global_financial_news()
    if df is None:
        log.error(f"获取全球股票新闻失败")
        return []
    news_list = []
    for index, row in df.iterrows():
        news = {
            "date": row["发布时间"],
            "title": row["标题"],
            "content": row["内容"]
        }
        news_list.append(news)
    return news_list

@lru_cache.cached("stock_sentiment", expire_seconds=60*60*24)
def get_stock_sentiment(symbol: str, market: str) -> List[Dict[str, Any]]:
    """
    获取股票情绪
    """
    log.info(f"开始获取股票情绪: {symbol}, {market}")
    market = market.lower()
    if market == 'cn': 
        news = _get_cn_stock_news(symbol)
        return news
    elif market == 'us' or market == 'hk':
        news = _get_us_hk_stock_news(symbol, market)
        return news
    else:
        raise ValueError(f"Invalid market: {market}")

if __name__ == "__main__":
    value = get_stock_sentiment("TSLA", "us")
    print(value)