from datetime import datetime, timedelta
import akshare as ak
import pandas as pd
import requests
from typing import Dict, Any, List
import logging
import os

log = logging.getLogger(__name__)

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
def get_financial_new_cn(limit: int = 20) -> pd.DataFrame:
    """
    获取最近的limit条新闻
    :param limit:
    :return:
    """
    df = ak.stock_hot_rank_em()
    df = df.sort_values(by="date", ascending=False)
    df = df.head(limit)
    return df

def get_news_from_newapi(keywords: List[str], limit: int = 20) -> Dict[str, Any]:
    """
    获取最新的limit条新闻
    :param keyword:
    :param limit:
    :return:
    """
    log.info(f"开始获取新闻: {keywords}, {limit}")
    date_str = (datetime.now()-timedelta(days=30)).strftime("%Y-%m-%d")
    if len(keywords) > 1:
        keywords_str = ' OR '.join(keywords)
    else:
        keywords_str = keywords[0]
    news_api_key = NEWS_API_KEY
    log.info(f"开始获取新闻: {keywords_str}, {date_str}")
    url = ('https://newsapi.org/v2/everything?'
       f'q={keywords_str}&'
       f'from={date_str}&'
       f'sortBy=popularity&'
       f'apiKey={news_api_key}')
    response = requests.get(url)
    log.info(f"获取到的响应: {response.json()}")
    if response.status_code == 200:
        json_data = response.json()
        status = json_data["status"]
        if status == "ok":
            if len(json_data["articles"]) > limit:
                return json_data["articles"][:limit]
            else:
                return json_data["articles"]
        else:
            return None
    else:
        return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    df = get_news_from_newapi(["美股:TSLA"], 10)
    print(df)