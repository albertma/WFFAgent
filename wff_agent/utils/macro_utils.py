from concurrent import futures
from typing import Any, Dict
from ..datasource import akshare_utils as akutils
import logging
log = logging.getLogger(__name__)           

def get_macro_data() -> Dict[str, Any]:
    """获取宏观数据
    Returns:
        Dict[str, Any]: 宏观数据
    """
    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_labor_df = executor.submit(akutils.get_labor_index)
        future_cpi_df = executor.submit(akutils.get_us_cpi)
        future_interest_rate_df = executor.submit(akutils.get_usa_interest_rate)
        us_labor_df = future_labor_df.result()
        cpi_df = future_cpi_df.result()
        interest_rate_df = future_interest_rate_df.result()
        us_labor_index = None
        if us_labor_df is not None:
            us_labor_index = us_labor_df.to_dict(orient="records")
        us_cpi = None
        if cpi_df is not None:
            us_cpi = cpi_df.to_dict(orient="records")
        us_interest_rate = None
        if interest_rate_df is not None:
            us_interest_rate = interest_rate_df.to_dict(orient="records")
    return {
        "美国劳动力指数": us_labor_index,
        "美国CPI": us_cpi,
        "美国利率": us_interest_rate
    }

  
