import logging

log = logging.getLogger(__name__)

def free_cash_flow_valuation(latest_fcf:int, recent_3_yr_fcf_avg_growth:float, 
                      discount_rate:float=0.09, growth_rate:float=0.01, shares_num:int=1)->dict:
    """
    计算自由现金流折现估值
    Args:
            latest_fcf (int): 最新自由现金流
            recent_3_yr_fcf_avg_growth (float): 最近3年自由现金流平均增长率
            discount_rate (float, optional): 折现率. Defaults to 0.09.
            growth_rate (float, optional): 增长率. Defaults to 0.01.
            shares_num (int, optional): 股票数量. Defaults to 1.
        Returns:
            dict: 自由现金流折现估值
    """
    log.info(f"DCF估值参数: latest_fcf: {latest_fcf}, recent_3_yr_fcf_avg_growth: {recent_3_yr_fcf_avg_growth}, discount_rate: {discount_rate}, growth_rate: {growth_rate}, shares_num: {shares_num}")
    if shares_num == 0 or shares_num == "None":
        log.error("股票数量为0")
        return None
    if latest_fcf <= 0:
        log.error("最新自由现金流为0")
        return None
    if recent_3_yr_fcf_avg_growth <= 0:
        log.error("最近3年自由现金流平均增长率为0,使用折现率作为增长率")
        recent_3_yr_fcf_avg_growth = discount_rate
    # 计算未来5年现金流
    future_5_yr_fcf = [latest_fcf*((1+recent_3_yr_fcf_avg_growth)**(i+1)) for i in range(5)]
    # 计算未来5年现金流折现值
    log.debug(f"to calc future_5_yr_discounted_fcf: {future_5_yr_fcf}")
    future_5_yr_discounted_fcf = [future_5_yr_fcf[i]/((1+discount_rate)**(i+1)) for i in range(5)]
    future_5_yr_discounted_fcf_sum = sum(future_5_yr_discounted_fcf)
        # 计算终值
    log.debug(f"to calc terminal_value: future_5_yr_fcf[-1]: {future_5_yr_fcf[-1]}, growth_rate: {growth_rate}, discount_rate: {discount_rate}")
    terminal_value = future_5_yr_fcf[-1]*(1 + growth_rate)/(discount_rate - growth_rate)
        # 折现到当前
    log.debug(f"to calc terminal_value_discounted: terminal_value: {terminal_value}, discount_rate: {discount_rate}")
    terminal_value_discounted = terminal_value/((1+discount_rate)**5)
    log.debug(f"to calc present_value: future_5_yr_discounted_fcf_sum: {future_5_yr_discounted_fcf_sum}, terminal_value_discounted: {terminal_value_discounted}")
    present_value = future_5_yr_discounted_fcf_sum + terminal_value_discounted
    log.debug(f"to return: present_value: {present_value}, shares_num: {shares_num}, intrinsic_value: {present_value/int(shares_num)}")
    log.info(f"dcf_valuation result: {present_value/int(shares_num)}")
    return {
        "latest_fcf": latest_fcf,
        "recent_3_yr_fcf_avg_growth": recent_3_yr_fcf_avg_growth,
        "present_value": present_value,
        "future_5_yr_fcf": future_5_yr_fcf,
        "intrinsic_value": present_value/int(shares_num)
    }