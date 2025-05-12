

from typing import Any, Dict
from ..datasource import alpha_v_utils as av_utils
from ..datasource import akshare_utils as ak_utils 
import logging

from . import ak_fin_utils, av_fin_utils

log = logging.getLogger(__name__)

def get_report_indicators(symbol: str, market: str, stock_price: float, 
                         discount_rate: float = 0.06, growth_rate: float = 0.02, shares_num: int = 1) -> Dict[str, Any]:
    """
    获取财务报表指标
    """
    if symbol is None:
        return {"error": f"""param symbol is None"""}
    if stock_price is None:
        return {"error": f"""param stock_price is None"""}
    if market is None or market not in ['us', 'cn', 'hk']:
        return {"error": f"""param market is not in ['us', 'cn', 'hk']"""}
    if discount_rate is None or discount_rate <= 0 or discount_rate >= 1:
        return {"error": f"""param discount_rate is not in (0, 1)"""}
    if growth_rate is None:
        return {"error": """param growth_rate is None"""}
    
    reports = None
    """财务关键指标计算"""
    if market == 'us':
        reports = av_utils.get_us_stock_financial_report(symbol) # type: ignore
    elif market == 'cn':
        reports = ak_utils.get_stock_financial_report_cn(symbol)
    elif market == 'hk':
        reports = ak_utils.get_stock_financial_report_hk(symbol)
    
    log.info(f"股票价格：{stock_price}, 开始计算{symbol}的财务指标")
    try:
        if market == 'us':
            indictors = av_fin_utils.calc_us_indicators(reports, stock_price, discount_rate=discount_rate, growth_rate=growth_rate)  
        elif market == 'cn':
            indictors = ak_fin_utils.calc_cn_indicators(reports, stock_price, discount_rate=discount_rate, growth_rate=growth_rate, shares_num=shares_num)  
        elif market == 'hk':
            indictors = ak_fin_utils.calc_hk_indicators(reports, stock_price, discount_rate=discount_rate, growth_rate=growth_rate, shares_num=shares_num)  
        log.debug(f"计算出的财务指标{symbol}, market:{market},indicators: {indictors}")
        return indictors
    except Exception as e:
        log.error(f"计算财务指标时发生错误: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    #indictors = get_report_indicators("000333", "cn", 75, 0.07, 0.01, 7600000000)
    #print(indictors)
    
    #indictors = get_report_indicators("00700", "hk", 495, 0.07, 0.02, 9200000000)
    # print(indictors)
    
    indictors = get_report_indicators("AAPL", "us", 209, 0.05, 0.01, 3490989083)
    print(indictors)