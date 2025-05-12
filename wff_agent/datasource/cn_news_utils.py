import akshare as ak
import pandas as pd


def get_financial_new(limit: int = 20) -> pd.DataFrame:
    """
    获取最近的limit条新闻
    :param limit:
    :return:
    """
    df = ak.stock_hot_rank_em()
    df = df.sort_values(by="date", ascending=False)
    df = df.head(limit)
    return df


if __name__ == "__main__":
    df = get_financial_new(limit=20)
    print(df)