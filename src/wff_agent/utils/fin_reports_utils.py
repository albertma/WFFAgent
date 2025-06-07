# -*- coding: utf-8 -*-

from typing import Any, Dict
from wff_agent.datasource import alpha_v_request as av_request
from wff_agent.datasource import akshare_request as ak_request 
import logging

from wff_agent.utils import ak_fin_utils, av_fin_utils

log = logging.getLogger(__name__)

def get_report_indicators(symbol: str, market: str, stock_price: float, 
                         discount_rate: float = 0.06, growth_rate: float = 0.02, shares_num: int = 1) -> Dict[str, Any]:
    """
    获取财务报表指标
    """
    if symbol is None:
        log.error(f"param symbol is None")
        return {"error": f"""param symbol is None"""}
    if stock_price is None:
        log.error(f"param stock_price is None")
        return {"error": f"""param stock_price is None"""}
    if market is None or market not in ['us', 'cn', 'hk']:
        log.error(f"param market is not in ['us', 'cn', 'hk']")
        return {"error": f"""param market is not in ['us', 'cn', 'hk']"""}
    if discount_rate is None or discount_rate <= 0 or discount_rate >= 1:
        log.error(f"param discount_rate is not in (0, 1)")
        return {"error": f"""param discount_rate is not in (0, 1)"""}
    if growth_rate is None:
        log.error(f"param growth_rate is None")
        return {"error": """param growth_rate is None"""}
    
    reports = None
    """财务关键指标计算"""
    log.info(f"股票价格：{stock_price}, 开始计算{symbol}的财务指标")
    try:
        if market == 'us':
            reports = av_request.get_stock_financial_report_us(symbol)
            indictors = av_fin_utils.calc_us_indicators(reports, stock_price, discount_rate=discount_rate, growth_rate=growth_rate)     
        elif market == 'cn':
            reports = ak_request.get_stock_financial_report_cn(symbol)
            indictors = ak_fin_utils.calc_cn_indicators(reports, stock_price, discount_rate=discount_rate, growth_rate=growth_rate, shares_num=shares_num)  
        elif market == 'hk':
            reports = ak_request.get_stock_financial_report_hk(symbol)
            indictors = ak_fin_utils.calc_hk_indicators(reports, stock_price, discount_rate=discount_rate, growth_rate=growth_rate, shares_num=shares_num)  
    except Exception as e:
        log.error(f"获取财务报表失败: {e}")
        return {"error": str(e)}
    
    log.info(f"计算财务指标完成: {symbol}, market:{market}")
    return indictors

if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)
    try:
        #indictors = get_report_indicators("000333", "cn", 75, 0.07, 0.01, 7600000000)
        #print(indictors)
        
        #indictors = get_report_indicators("00700", "hk", 495, 0.07, 0.02, 9200000000)
        # print(indictors)
        
        indictors = get_report_indicators("AAPL", "us", 209, 0.05, 0.01, 3490989083)
        print(indictors)
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序发生错误: {e}")
    finally:
        print("程序执行完成")
        exit(0)