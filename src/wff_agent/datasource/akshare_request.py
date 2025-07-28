from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
import json
import akshare as ak
from typing import Dict, Any, List
import pandas as pd
import datetime
import logging
from wff_agent.datasource import file_lru_cache as filecache

log = logging.getLogger(__name__)

def get_cn_stock_info(symbol: str) -> Dict[str, Any]:
    """
    获取股票价格
    Args:
        symbol: 股票代码（如：000001，不带市场前缀）

    Returns:
    {'最新': 76.58, '股票代码': '000333', '股票简称': '美的集团', '总股本': 7664608384.0, '流通股': 6901132047.0, '总市值': 586955710046.72, '流通市值': 528488692159.26, '行业': '家电行业', '上市时间': 20130918}
        股票基本信息字典，包含以下字段:
        - 最新
        - 股票代码
        - 股票简称
        - 总股本
        - 流通股
        - 总市值
        - 流通市值
        - 行业
        - 上市时间
    """
    stock_info_df = ak.stock_individual_info_em(symbol)
    info_dict = {}
    for _, row in stock_info_df.iterrows():
        info_dict[row['item']] = row['value']
    return info_dict

def get_hk_stock_info(symbol: str) -> Dict[str, Any]:
    """
    获取香港股票信息
    Args:
        symbol: 股票代码（如：000001，不带市场前缀）

    Returns:
        股票基本信息字典，包含以下字段:
        - 日期
        - 开盘
        - 收盘
        - 最高
        - 最低
        - 成交量
        - 成交额
        - 振幅
       
    """
    start_date = (datetime.datetime.now() - datetime.timedelta(days=10)).strftime("%Y%m%d")
    end_date = datetime.datetime.now().strftime("%Y%m%d")
    stock_info_df = ak.stock_hk_hist(symbol,period="daily", start_date=start_date,end_date=end_date, adjust="qfq")
    stock_info_df = stock_info_df.tail(1)
    stock_info_df["日期"] = stock_info_df["日期"].astype(str)
    
    value = stock_info_df.to_dict(orient="records")
    return value[0]

def convert2chinese_column(df)-> pd.DataFrame:
    """
    将DataFrame中的列名转换为中文

    Args:
        df: 要转换的DataFrame   
    Returns:
        转换后的DataFrame
    """
    column_mapping = {
    'date': '日期',
    'open': '开盘',
    'high': '最高',
    'low': '最低',
    'close': '收盘',
    'volume': '成交量'  # 新增的列名映射
    }
    df = df.rename(columns=column_mapping)
    return df
@filecache.cached("stock_history", expire_seconds=60*60*8)
def get_stock_history(symbol: str, market: str, period: str = "daily", 
                     start_date: str = None, end_date: str = None,
                     adjust: str = "qfq") -> pd.DataFrame:
    """
    获取股票历史行情数据
    
    Args:
        symbol: 股票代码（如：000001，不带市场前缀）
        market: 市场，可选 us, hk, cn
        period: 时间周期，可选 daily, weekly, monthly
        start_date: 开始日期，格式 YYYYMMDD，默认为近一年
        end_date: 结束日期，格式 YYYYMMDD，默认为今天
        adjust: 复权类型，qfq: 前复权, hfq: 后复权, 空: 不复权
        
    Returns:
        股票历史数据DataFrame
    """
    try:
        # 设置默认日期
        log.info(f"start_date: {start_date}, end_date: {end_date}")
        market = market.lower()
        symbol = symbol.upper()
        if not end_date:
            end_date = datetime.datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime("%Y%m%d")
        log.info(f"获取股票历史数据: {symbol}, {period}, {start_date}, {end_date}, {adjust}")
        df = None
        with ThreadPoolExecutor() as executor:
            if market == 'us':
                log.info(f"获取美股历史数据: {symbol}")
                future = executor.submit(ak.stock_us_daily, symbol=symbol, adjust=adjust)
                df = future.result()
                df = convert2chinese_column(df)
            elif market == 'hk':
                log.info(f"获取HK股历史数据: {symbol}")
                future = executor.submit(ak.stock_hk_hist, symbol=symbol, period=period, start_date=start_date,end_date=end_date, adjust=adjust)
                df = future.result()
            elif market == 'cn':
                log.info(f"获取A股历史数据: {symbol}")
                future = executor.submit(ak.stock_zh_a_hist, symbol=symbol, period=period, start_date=start_date,end_date=end_date, adjust=adjust)
                df = future.result()
                
        if df is None or df.empty:
            log.error(f"获取股票历史数据为空: {symbol}")
            raise ValueError(f"获取股票历史数据为空: {symbol}")
            
        # 重命名列，确保列名为小写
        df.columns = [col.lower() for col in df.columns]
        
        # 处理日期列并转换为索引
        date_columns = ['日期', 'date']
        date_col = next((col for col in date_columns if col in df.columns), None)
        
        if date_col:
            # 确保日期格式一致
            if isinstance(df[date_col].iloc[0], str):
                df[date_col] = pd.to_datetime(df[date_col])
            df = df.set_index(date_col)
        
        # 确保数值列是浮点数
        numeric_cols = ['开盘', '收盘', '最高', '最低', '成交量', '涨跌幅', '涨跌额', '振幅', '换手率']
        for col in [c.lower() for c in numeric_cols]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')       
        return df
    except Exception as e:
        print(f"获取股票历史数据时出错: {e}")
        raise ValueError(f"获取股票历史数据时出错: {e}")
    
@filecache.cached("cn_stock_financial_report", expire_seconds=60*60*24*30)
def get_stock_financial_report_cn(symbol: str) -> dict:
    """
    获取股票财务指标
    
    Args:
        symbol: 股票代码（如：000001，不带市场前缀）
        
    Returns:
        股票财务指标DataFrame
    """
    
    log.info(f"get_stock_financial_report_cn: {symbol}")    
    try:
        # 获取财务指标
        # download 3 type report at same time and wait to them all completed
        # 资产负债表
        def get_balance_sheet():
            log.info(f"get_balance_sheet: {symbol}")
            return ak.stock_financial_report_sina(stock=symbol, symbol="资产负债表")
        def get_income_statement():
            log.info(f"get_income_statement: {symbol}")
            return ak.stock_financial_report_sina(stock=symbol, symbol="利润表")
        def get_cash_flow_statement():
            log.info(f"get_cash_flow_statement: {symbol}")
            return ak.stock_financial_report_sina(stock=symbol, symbol="现金流量表")
        with ThreadPoolExecutor() as executor:
            log.info("ThreadPoolExecutor")
            future_to_symbol = {executor.submit(get_balance_sheet): "资产负债表",
                                executor.submit(get_income_statement): "利润表",
                                executor.submit(get_cash_flow_statement): "现金流量表"}
            for future in as_completed(future_to_symbol):
                current_report_type = future_to_symbol[future]
                try:
                    data = future.result()
                except Exception as exc:
                    log.error('%r generated an exception: %s' % (current_report_type, exc))
                    raise ValueError(f"获取股票财务指标时出错: {exc}")
                else:
                    log.info('%r page is %d bytes' % (current_report_type, len(data)))
                    if current_report_type == "资产负债表":
                        balance_sheet = data
                    elif current_report_type == "利润表":
                        income_statement = data
                    elif current_report_type == "现金流量表":
                        cash_flow_statement = data
        # 合并财务指标
        if balance_sheet is None:
            raise ValueError(f"获取股票财务balance_sheet时出错: {symbol}")
        if income_statement is None:
            raise ValueError(f"获取股票财务income_statement时出错: {symbol}")
        if cash_flow_statement is None:
            raise ValueError(f"获取股票财务cash_flow_statement时出错: {symbol}")
        dict = {
            "balance_sheet": balance_sheet,
            "income_statement": income_statement,
            "cashflow": cash_flow_statement,
        }
        
        return dict
    except Exception as e:
        print(f"获取股票财务指标时出错: {e}")
        raise ValueError(f"获取股票财务指标时出错: {e}")
    
@filecache.cached("stock_financial_report_hk", expire_seconds=60*60*24*30)
def get_stock_financial_report_hk(symbol: str) -> dict:
    balance_sheet = None
    income_statement = None
    cash_flow_statement = None
    with ThreadPoolExecutor() as executor:
        balance_sheet = executor.submit(ak.stock_financial_hk_report_em, stock=symbol, symbol="资产负债表", indicator="年度")
        income_statement = executor.submit(ak.stock_financial_hk_report_em, stock=symbol, symbol="利润表", indicator="年度")
        cash_flow_statement = executor.submit(ak.stock_financial_hk_report_em, stock=symbol, symbol="现金流量表", indicator="年度")
        quarter_balance_sheet = executor.submit(ak.stock_financial_hk_report_em, stock=symbol, symbol="资产负债表", indicator="季度")
        quarter_income_statement = executor.submit(ak.stock_financial_hk_report_em, stock=symbol, symbol="利润表", indicator="季度")
        quarter_cash_flow_statement = executor.submit(ak.stock_financial_hk_report_em, stock=symbol, symbol="现金流量表", indicator="季度")
    
    balance_sheet_result = transform_hk_financial_report(balance_sheet.result())
    income_statement_result = transform_hk_financial_report(income_statement.result())
    cash_flow_statement_result = transform_hk_financial_report(cash_flow_statement.result())
    quarter_balance_sheet_result = transform_hk_financial_report(quarter_balance_sheet.result())
    quarter_income_statement_result = transform_hk_financial_report(quarter_income_statement.result())
    quarter_cash_flow_statement_result = transform_hk_financial_report(quarter_cash_flow_statement.result())
    log.info(f"获取港股财务指标: {symbol} 成功")
    return {
        "balance_sheet": balance_sheet_result,
        "income_statement": income_statement_result,
        "cashflow": cash_flow_statement_result,
        "quarter_balance_sheet": quarter_balance_sheet_result,
        "quarter_income_statement": quarter_income_statement_result,
        "quarter_cashflow": quarter_cash_flow_statement_result
    }

def get_macro_data() -> dict:
    """
    获取宏观数据
    """
    macro_china_ppi_yearly_df = ak.macro_china_ppi_yearly()
    macro_china_cpi_yearly_df = ak.macro_china_cpi_yearly()
    macro_china_cx_services_pmi_yearly_df = ak.macro_china_cx_services_pmi_yearly()
    macro_usa_cpi_monthly_df = ak.macro_usa_cpi_monthly()
    macro_usa_labor_df = ak.macro_usa_lmci()
    macro_bank_usa_interest_rate_df = ak.macro_bank_usa_interest_rate()
    return {
        "macro_china_ppi_yearly": json.dumps(macro_china_ppi_yearly_df, ensure_ascii=False, orient="records"),
        "macro_china_cpi_yearly": json.dumps(macro_china_cpi_yearly_df, ensure_ascii=False, orient="records"),
        "macro_china_cx_services_pmi_yearly": json.dumps(macro_china_cx_services_pmi_yearly_df, ensure_ascii=False, orient="records"),
        "macro_usa_cpi_monthly": json.dumps(macro_usa_cpi_monthly_df, ensure_ascii=False, orient="records"),
        "macro_usa_labor": json.dumps(macro_usa_labor_df, ensure_ascii=False, orient="records"),
        "macro_bank_usa_interest_rate": json.dumps(macro_bank_usa_interest_rate_df, ensure_ascii=False, orient="records"),
    }

      
def transform_hk_financial_report(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    将港股财务报表转换为字典格式，合并相同报告日期的数据
    
    Args:
        df (pd.DataFrame): 港股财务报表数据框
        
    Returns:
        dict: 转换后的财务报告数据 
    """
    # 确保REPORT_DATE列是日期时间格式
    df['REPORT_DATE'] = pd.to_datetime(df['REPORT_DATE'])
    df.fillna(0, inplace=True)
    df.sort_values(by="REPORT_DATE", inplace=True, ascending=False)
    df = df.head(5)
    # 按REPORT_DATE分组
    grouped = df.groupby('REPORT_DATE')
    
    # 创建结果字典
    result = []
    
    # 遍历每个报告日期
    for date, group in grouped:
        # 创建该日期的报告对象
        report = {
            "report_time": date.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 遍历该日期的所有行
        for _, row in group.iterrows():
            # 使用STD_ITEM_NAME作为键，AMOUNT作为值
            if 'STD_ITEM_NAME' in row and 'AMOUNT' in row:
                report[row['STD_ITEM_NAME']] = row['AMOUNT']
        
        # 将报告添加到结果中
        result.append(report)
    # 返回最后5条记录
    return json.dumps(result, ensure_ascii=False)
    
        
 
def get_cn_bid_ask_stock(symbol: str) -> dict:
    stock_bid_ask_em_df = ak.stock_bid_ask_em(symbol=symbol)
    return stock_bid_ask_em_df


def is_valid_us_stock_symbols(symbol:str) -> bool:
    symbol_list = _get_us_stock_symbol()
    lower_target = symbol.lower()
    contains = any(s.lower() == lower_target for s in symbol_list)
    return contains

@filecache.cached("us_stock_symbols", expire_seconds=60*60*24*90)
def _get_us_stock_symbol()-> list:
    df = ak.get_us_stock_name()
    symbol_list = df['symbol'].tolist()
    return symbol_list

@filecache.cached("us_stock_code_symbol", expire_seconds=60*60*24*90)  
def _get_us_stock_code_symbol()-> pd.DataFrame:
    stock_us_spot_em_df = ak.stock_us_spot_em()
    
    print(stock_us_spot_em_df)
    return stock_us_spot_em_df

def transfer_df_to_dict(df: pd.DataFrame) -> dict: 
    return df.to_json(force_ascii=False,orient="records")

def get_cn_stock_valuation(symbol: str) -> dict:
    """
    获取股票估值指标

    Args:
        symbol: 股票代码（如：000001，不带市场前缀）

    Returns:
        股票估值指标DataFrame
    """
    stock_a_indicator_lg_df = ak.stock_a_indicator_lg(symbol=symbol)
    return stock_a_indicator_lg_df
@filecache.cached("cn_market_activity", expire_seconds=60*60*24*365)
def get_cn_market_activity(date:str) -> dict:
    """
    获取市场情绪指标
    Returns:
        市场情绪指标DataFrame
    """
    stock_market_activity_legu_df = ak.stock_market_activity_legu()
    market_activity = transfer_df_to_dict(stock_market_activity_legu_df)
    return market_activity

@filecache.cached("cn_market_sentiment", expire_seconds=60*60*24*365)
def get_cn_market_sentiment(date:str) -> dict:
    """_summary_

    Args:
        date (str): _description_

    Returns:
        dict: _description_
    """
    stock_zt_pool_em_df = ak.stock_zt_pool_em(date=date)
    zt_pool = transfer_df_to_dict(stock_zt_pool_em_df)
    stock_zt_pool_zbgc_em_df = ak.stock_zt_pool_zbgc_em(date=date)
    zbgc_pool= transfer_df_to_dict(stock_zt_pool_zbgc_em_df)
    return {
        "zt_pool": zt_pool,
        "zt_pool_zbgc": zbgc_pool
    }
@filecache.cached("cn_news_from_eastmoney", expire_seconds=60*60*8)
def get_cn_news_from_eastmoney(symbol: str) -> pd.DataFrame:
    """
    获取东方财富网的新闻
    """
    news_df = ak.stock_news_em(symbol=symbol)
    return news_df

@filecache.cached("get_global_financial_news", expire_seconds=60*60*5)
def get_global_financial_news() -> pd.DataFrame:
    """
    获取全球股票新闻
    """
    stock_info_global_futu_df = ak.stock_info_global_futu()
    return stock_info_global_futu_df


def get_cn_ppi() -> pd.DataFrame:
    macro_china_ppi_yearly_df = ak.macro_china_ppi_yearly()
    macro_china_ppi_yearly_df.sort_values(by="日期", inplace=True, ascending=False)
    macro_china_ppi_yearly_df = macro_china_ppi_yearly_df.head(12)
    return macro_china_ppi_yearly_df

def get_cn_cpi() -> pd.DataFrame:
    macro_china_cpi_yearly_df = ak.macro_china_cpi_yearly()
    macro_china_cpi_yearly_df.sort_values(by="日期", inplace=True, ascending=False)
    macro_china_cpi_yearly_df = macro_china_cpi_yearly_df.head(12)
    return macro_china_cpi_yearly_df

def get_cn_cx_pmi() -> pd.DataFrame:
    macro_china_cx_services_pmi_yearly_df = ak.macro_china_cx_services_pmi_yearly()
    macro_china_cx_services_pmi_yearly_df.sort_values(by="日期", inplace=True, ascending=False)
    macro_china_cx_services_pmi_yearly_df = macro_china_cx_services_pmi_yearly_df.head(12)
    return macro_china_cx_services_pmi_yearly_df


def get_us_cpi() -> pd.DataFrame:
    """
    获取美国CPI数据
            商品        日期   今值  预测值   前值
0    美国CPI月率  1970-01-01  0.5  NaN  NaN
1    美国CPI月率  1970-02-01  0.5  NaN  0.5
2    美国CPI月率  1970-03-01  0.5  NaN  0.5
3    美国CPI月率  1970-04-01  0.5  NaN  0.5
4    美国CPI月率  1970-05-01  0.5  NaN  0.5
    """
    macro_usa_cpi_monthly_df = ak.macro_usa_cpi_monthly()
    macro_usa_cpi_monthly_df.sort_values(by="日期", inplace=True, ascending=False)
    macro_usa_cpi_monthly_df = macro_usa_cpi_monthly_df.head(5)
    return macro_usa_cpi_monthly_df

def get_labor_index() -> pd.DataFrame:
    """
    获取美国劳工指数
       商品          日期   今值  预测值   前值
0   美联储劳动力市场状况指数  2014-10-06  2.5  NaN  NaN
1   美联储劳动力市场状况指数  2014-11-10  4.0  NaN  4.0
2   美联储劳动力市场状况指数  2014-12-08  2.9  NaN  3.9
3   美联储劳动力市场状况指数  2015-01-12  6.1  NaN  5.5
    """
    macro_usa_labor_df = ak.macro_usa_lmci()
    macro_usa_labor_df.sort_values(by="日期", inplace=True, ascending=False)
    macro_usa_labor_df = macro_usa_labor_df.head(5)
    return macro_usa_labor_df

def get_usa_interest_rate() -> pd.DataFrame:
    """
    获取美国利率数据
       商品          日期     今值   预测值     前值
0    美联储利率决议报告  1982-09-28  10.25   NaN    NaN
1    美联储利率决议报告  1982-10-02  10.00   NaN  10.25
2    美联储利率决议报告  1982-10-08   9.50   NaN  10.00
3    美联储利率决议报告  1982-11-20   9.00   NaN   9.50
4    美联储利率决议报告  1982-12-15   8.50   NaN   9.00
    """
    macro_bank_usa_interest_rate_df = ak.macro_bank_usa_interest_rate()
    macro_bank_usa_interest_rate_df.sort_values(by="日期", inplace=True, ascending=False)
    macro_bank_usa_interest_rate_df = macro_bank_usa_interest_rate_df.head(5)
    return macro_bank_usa_interest_rate_df

def get_global_index()-> pd.DataFrame:
    """
    获取全球指数
    """
    index_global_spot_em_df = ak.index_global_spot_em()
    return index_global_spot_em_df

def get_cn_index_spot()-> pd.DataFrame:
    """
    获取中国指数
          代码      名称         最新价      涨跌额    涨跌幅         昨收          今开          最高          最低         成交量           成交额
0    sh000001    上证指数   3369.2445   27.246  0.815  3341.9989   3352.9698   3372.4724   3344.2687   418239910  522080702357
1    sh000002    Ａ股指数   3531.1275   28.600  0.817  3502.5275   3513.9838   3534.5412   3504.8483   417936404  521540467982
2    sh000003    Ｂ股指数    261.9789    1.927  0.741   260.0522    261.0472    261.9982    260.1937      231079      91312441
3    sh000004    工业指数   2907.2801   28.002  0.973  2879.2781   2891.7333   2908.7765   2886.0582   257242319  384813165404
4    sh000005    商业指数   2642.7401   20.328  0.775  2622.4119   2627.1508   2643.0980   2617.9914    35696940   33925149295
    """
    stock_zh_index_spot_sina_df = ak.stock_zh_index_spot_sina()
    return stock_zh_index_spot_sina_df[stock_zh_index_spot_sina_df["名称"].isin(["上证指数", "深圳成指", "创业板指", "沪深300", "中证500"])]

def get_us_stock_spot()-> pd.DataFrame:
    """
    获取美国股票
    """
    stock_us_spot_em_df = ak.stock_us_spot_em()
    return stock_us_spot_em_df
if __name__ == "__main__":
    #data = get_cn_stock_info("000333")
    #print(data)
    # df = get_stock_history(symbol="baba", market="us", period="daily", start_date="20250101", end_date="20250502")
    # print(df)
    # df = get_stock_history(symbol="01810", market="hk", period="daily")
    # print(df)
    # df = _get_us_stock_code_symbol()
    # reports = get_stock_financial_report_cn("603160")
    # #print(reports)
    # print(reports["balance_sheet"].head(2).to_json(force_ascii=False ,orient="records"))
    # print(reports["income_statement"].head(20).to_json(force_ascii=False ,orient="records"))
    # print(reports["cashflow"].head(2).to_json(force_ascii=False ,orient="records"))
    # print(reports["quarter_balance_sheet"].head(2).to_json(force_ascii=False ,orient="records"))
    # print(reports["quarter_income_statement"].head(2).to_json(force_ascii=False ,orient="records"))
    # print(reports["quarter_cashflow"].head(2).to_json(force_ascii=False ,orient="records"))
    
    # stock_market_activity_legu_df = ak.stock_market_activity_legu()
    # print(stock_market_activity_legu_df)
    # current_date_str = datetime.datetime.now().strftime("%Y%m%d")
    # data = get_cn_market_activity(current_date_str)
    # print(data)
    # data = get_cn_market_sentiment(current_date_str)
    # print(data)
    # stock_rank_xstp_ths_df = ak.stock_rank_xstp_ths(symbol="5日均线")
    # print(stock_rank_xstp_ths_df)
    # current_date_str = datetime.datetime.now().strftime("%Y%m%d")
    # data = get_cn_market_sentiment(current_date_str)
    # print(data)
    # data = get_stock_financial_report_hk("00700")
    # print(json.dumps(data, ensure_ascii=False))
    
    #print(stock_financial_hk_report_em_df.head(5).to_json(force_ascii=False, orient="records"))
    data = get_macro_data()
    print(data)

   
    