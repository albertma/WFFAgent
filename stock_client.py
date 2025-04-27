import yfinance as yf
import os
import requests

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY") 
def get_stock_price_yf(symbol):
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1d", interval="1m")  # 获取最近1分钟数据
    return data['Close'].iloc[-1] if not data.empty else None

def get_stock_price_vantage(symbol):
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
    response = requests.get(url)
    data = response.json()
    try:
        return float(data["Global Quote"]["05. price"])
    except KeyError:
        return "请求失败：请检查API密钥或股票代码"


# 调用示例
if __name__ == "__main__":
    symbol = "AAPL"
    price = get_stock_price_vantage(symbol)
    print(f"AAPL 当前股价：${price:.2f}")