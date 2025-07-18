from datetime import datetime
import json
import math
import numpy as np
import pandas as pd
from wff_agent.utils import fcf_valuation
import logging
log = logging.getLogger(__name__)

def _cn_df_to_dict(df: pd.DataFrame) -> dict: 
    df.sort_values(by="报告日", inplace=True, ascending=False)
    return df.to_json(force_ascii=False,orient="records")

def calc_cn_indicators(data: dict, stock_price:float, 
                       discount_rate:float=0.09, 
                       growth_rate:float=0.01, shares_num:int=1) -> dict:
    """
    计算财务指标
    Args:
        data (dict): 财务数据
        stock_price (float): 股票价格
        discount_rate (float, optional): 折现率. Defaults to 0.09.
        growth_rate (float, optional): 增长率. Defaults to 0.01.
    Returns:
        dict: 财务指标
    """
    log.info(f"计算财务指标 calc_cn_indicators")
    annual_balance_sheet = _filter_annual_report(data["balance_sheet"])
    annual_income_statement = _filter_annual_report(data["income_statement"])
    annual_cash_flow_statement = _filter_annual_report(data["cashflow"])
    
    quarter_balance_sheet = _filter_quarter_report(data["balance_sheet"])
    quarter_income_statement = _filter_quarter_report(data["income_statement"])
    quarter_cash_flow_statement = _filter_quarter_report(data["cashflow"])
    # 计算财务指标
    fin_ratios = _calc_fin_cn_ratio(annual_balance_sheet, annual_income_statement, annual_cash_flow_statement, stock_price)
    quarter_fin_ratios = _calc_fin_cn_ratio(quarter_balance_sheet, quarter_income_statement, quarter_cash_flow_statement, stock_price)
    # 计算自由现金流分析
    fcf_growth_rate = np.mean(fin_ratios["free_cash_flow_growth"])
    fcf_analysis = fcf_valuation.free_cash_flow_valuation(fin_ratios["free_cash_flow"][-1], 
                                                          fcf_growth_rate, 
                                                          discount_rate, growth_rate, shares_num)
    if fcf_analysis is None:
        return {
            "annual_financial_report_indicators": fin_ratios,
            "quarter_financial_report_indicators":quarter_fin_ratios, 
        }
    else:
        return {
            "annual_financial_report_indicators": fin_ratios,
            "quarter_financial_report_indicators":quarter_fin_ratios,
            "dcf_valuation": fcf_analysis
        }

def calc_hk_indicators(data: dict, stock_price:float, 
                       discount_rate:float=0.09, 
                       growth_rate:float=0.01, shares_num:int=1) -> dict:
    """
    计算财务指标
    Args:
        data (dict): 财务数据
        stock_price (float): 股票价格
        discount_rate (float, optional): 折现率. Defaults to 0.09.
        growth_rate (float, optional): 增长率. Defaults to 0.01.
        shares_num (int, optional): 股数. Defaults to 1.
    Returns:
        dict: 财务指标
    """
    logging.info(f"计算财务指标 calc_hk_indicators")
    annual_balance_sheet = data["balance_sheet"]
    annual_income_statement = data["income_statement"]
    annual_cash_flow_statement = data["cashflow"]
    quarter_balance_sheet = data["quarter_balance_sheet"]
    quarter_income_statement = data["quarter_income_statement"]
    quarter_cash_flow_statement = data["quarter_cashflow"]
    
    # 计算财务指标
    fin_ratios = _calc_fin_hk_ratio(annual_balance_sheet, annual_income_statement, annual_cash_flow_statement, stock_price)
    quarter_fin_ratios = _calc_fin_hk_ratio(quarter_balance_sheet, quarter_income_statement, quarter_cash_flow_statement, stock_price)
    fcf_analysis = fcf_valuation.free_cash_flow_valuation(
        fin_ratios["free_cash_flow"][-1], 
        np.mean(fin_ratios["free_cash_flow_growth"]),  
        discount_rate, 
        growth_rate, 
        shares_num)
    if fcf_analysis is None:
        return {
            "annual_financial_report_indicators": fin_ratios,
            "quarter_financial_report_indicators": quarter_fin_ratios,
        }
    else:
        return {
            "annual_financial_report_indicators": fin_ratios,
            "quarter_financial_report_indicators": quarter_fin_ratios,
            "dcf_valuation": fcf_analysis
        }
        

def _filter_annual_report(report: pd.DataFrame)-> dict:
    """
    过滤年度报告
    Args:
        report (pd.DataFrame): 年度报告
    Returns:
        dict: 年度报告
    """
    log.info(f"过滤年度报告 _filter_annual_report")
    report['报告日'] = pd.to_datetime(report['报告日'])
    report.fillna(0, inplace=True)
    annual_report = report[report['报告日'].dt.month == 12]
    log.info(f"过滤年度报告 _filter_annual_report size: {len(annual_report)}")
    if len(annual_report) > 0:
        annual_report = annual_report.head(7)
        log.debug(f"过滤年度报告 _filter_annual_report: \n{annual_report}")
        return _cn_df_to_dict(annual_report)
    else:
        log.debug(f"过滤年度报告 _filter_annual_report: \n{annual_report}")
        return _cn_df_to_dict(annual_report)  
def _filter_quarter_report(report: pd.DataFrame)-> dict:
    """
    过滤季度报告
    """
    report['报告日'] = pd.to_datetime(report['报告日'])
    report.fillna(0, inplace=True)
    report.sort_values(by="报告日", inplace=True, ascending=False)
    report = report.head(6)
    return _cn_df_to_dict(report)

def _calc_growth_rate(current_value: float, previous_value: float) -> float:
    """
    计算增长率
    Args:
        current_value (float): 当前值
        previous_value (float): 上一个值
    Returns:
        float: 增长率
    """
    if previous_value == 0:
        return 0
    return round((current_value - previous_value) / previous_value, 4)
def _calc_ratio(part: float, whole: float) -> float:
    """
    计算比例
    Args:
        part (float): 部分
        whole (float): 整体
    Returns:
        float: 比例
    """
    if whole == 0:
        return None
    return round(part / whole, 4)
def _calc_ratio_with_keys(part_element: dict, part_key: str, whole_element: dict, whole_key: str) -> float:
    """
    计算比例
    """
    if part_element.keys().__contains__(part_key) and whole_element.keys().__contains__(whole_key):
        return round(_calc_ratio(part_element[part_key], whole_element[whole_key]), 4)
    else:
        return 0
# 计算财务指标
def _calc_fin_cn_ratio(balance_sheet: dict, 
                    income_statement: dict, 
                    cash_flow_statement: dict, 
                    current_price:float):
    """计算财务指标

    Args:
        balance_sheet (dict): 资产负债表
        income_statement (dict): 利润表
        cash_flow_statement (dict): 现金流量表
        current_price (float): 当前股价

    Returns:
        dict: 财务指标
    """
    balance_sheet = json.loads(balance_sheet)
    income_statement = json.loads(income_statement)
    cash_flow_statement = json.loads(cash_flow_statement)
    balance_sheet.sort(key=lambda x: x['报告日'], reverse=True)
    income_statement.sort(key=lambda x: x['报告日'], reverse=True)
    cash_flow_statement.sort(key=lambda x: x['报告日'], reverse=True)
    log.debug(f"cal revenue growth")
    revenue_growth = [_calc_growth_rate(income_statement[i]['营业总收入'], income_statement[i+1]['营业总收入']) for i in range(len(income_statement)-1)]
    log.info(f"cal gross margin:{income_statement}")
    gross_margin = [1-_calc_ratio(income_statement[i]['营业成本'], income_statement[i]['营业收入']) for i in range(len(income_statement))]
    
    # 计算资产负债表的财务比率
    log.debug(f"cal management expense ratio")
    management_expense_ratio = [_calc_ratio(income_statement[i]['管理费用'], income_statement[i]['营业收入']) for i in range(len(income_statement))]
    log.debug(f"cal sale expense ratio")
    sale_expense_ratio = [_calc_ratio(income_statement[i]['销售费用'], income_statement[i]['营业收入']) for i in range(len(income_statement))]
    log.debug(f"cal operating expense ratio")
    operating_expense_ratio = [_calc_ratio(income_statement[i]['营业成本'], income_statement[i]['营业收入']) for i in range(len(income_statement))]
    log.debug(f"cal dev expense ratio")
    dev_expense_ratio = [_calc_ratio(income_statement[i]['研发费用'], income_statement[i]['营业收入']) for i in range(len(income_statement))]
    log.debug(f"cal fin cost ratio")
    fin_cost_ratio = [_calc_ratio(income_statement[i]['财务费用'], income_statement[i]['营业收入']) for i in range(len(income_statement))]
    total_expense_ratio = [_calc_ratio(income_statement[i]['财务费用']+income_statement[i]['研发费用']+ income_statement[i]['销售费用']+income_statement[i]['管理费用'], income_statement[i]['营业收入']) for i in range(len(income_statement))]
    
    # 固定资产占比，流动资产占比，流动负债占比，长期负债占比
    log.debug(f"cal fixed assets ratio")
    fixed_assets_ratio = [_calc_ratio(balance_sheet[i]['固定资产及清理合计'], balance_sheet[i]['资产总计']) for i in range(len(balance_sheet))]
    log.debug(f"cal current assets ratio")
    current_assets_ratio = [_calc_ratio(balance_sheet[i]['流动资产合计'], balance_sheet[i]['资产总计']) for i in range(len(balance_sheet))]
    log.debug(f"cal current liabilities ratio")
    current_liabilities_ratio = [_calc_ratio(balance_sheet[i]['流动负债合计'], balance_sheet[i]['资产总计']) for i in range(len(balance_sheet))]
    log.debug(f"cal long liabilities ratio")
    long_liabilities_ratio = [_calc_ratio(balance_sheet[i]['长期借款']+balance_sheet[i]["长期应付款合计"], balance_sheet[i]['资产总计']) for i in range(len(balance_sheet))]
    
    # 资产周转率，存货周转率，应收账款周转率，应付账款周转率，利息覆盖率=ebit/利息支出
    log.debug(f"cal asset turnover ratio")
    asset_turnover_ratio = [_calc_ratio(income_statement[i]['营业收入'], balance_sheet[i]['资产总计']) for i in range(len(balance_sheet))]
    log.debug(f"cal inventory turnover ratio")
    inventory_turnover_ratio = [_calc_ratio(income_statement[i]['营业收入'], balance_sheet[i]['存货']) for i in range(len(balance_sheet))]
    log.debug(f"cal receivables turnover ratio")
    receivables_turnover_ratio = [_calc_ratio(income_statement[i]['营业收入'], balance_sheet[i]['应收账款']) for i in range(len(balance_sheet))]
    log.debug(f"cal payables turnover ratio")
    payables_turnover_ratio = [_calc_ratio(income_statement[i]['营业收入'], balance_sheet[i]['应付账款']) for i in range(len(balance_sheet))]
    interest_coverage_ratio = [_calc_ratio(income_statement[i]['营业利润'], income_statement[i]['利息支出']) for i in range(len(balance_sheet))]
    log.debug(f"cal free cash flow: {cash_flow_statement}")        
    # 自由现金流，自由现金流变化率，自由现金流占销售收入的比值
    free_cash_flow = [cash_flow_statement[i]['经营活动产生的现金流量净额'] - cash_flow_statement[i]['购建固定资产、无形资产和其他长期资产所支付的现金'] for i in range(len(balance_sheet))]
    free_cash_flow_growth = [_calc_growth_rate(free_cash_flow[i], free_cash_flow[i+1]) for i in range(len(free_cash_flow)-1)]
    free_cash_flow_ratio = [_calc_ratio(free_cash_flow[i], income_statement[i]['营业收入']) for i in range(len(free_cash_flow))]
    # ROE（包括净利润率=Net Income/Revenue，总资产周转率=Revenue/Avg Assets， 权益乘数=Avg Assets / Avg Shareholder Equity）
    log.debug(f"cal net margin ratio: {income_statement}")
    net_margin_ratio = [_calc_ratio(income_statement[i]['净利润'], income_statement[i]['营业收入']) for i in range(len(income_statement))]
    log.debug(f"cal asset turnover ratio")
    asset_turnover_ratio = [_calc_ratio(income_statement[i]['营业收入'], balance_sheet[i]['资产总计']) for i in range(len(balance_sheet))]
    log.debug(f"cal equity multiplier")
    equity_multiplier = [_calc_ratio(balance_sheet[i]['资产总计'], balance_sheet[i]['所有者权益(或股东权益)合计']) for i in range(len(balance_sheet))]
    roe = [round(net_margin_ratio[i]*asset_turnover_ratio[i]*equity_multiplier[i],2) for i in range(len(balance_sheet))]
    roe = [str(item*100)+"%" for item in roe]
    log.debug(f"cal asset debt ratio")
    # 资产负债率，流动比率，速动比率
    asset_debt_ratio = [_calc_ratio(balance_sheet[i]['负债合计'], balance_sheet[i]['资产总计']) for i in range(len(balance_sheet))]
    current_ratio = [_calc_ratio(balance_sheet[i]['流动资产合计'], balance_sheet[i]['负债合计']) for i in range(len(balance_sheet))]
    quick_ratio = [_calc_ratio(balance_sheet[i]['流动资产合计'], balance_sheet[i]['流动负债合计']) for i in range(len(balance_sheet))]
    # 经营活动现金流量净额，投资活动现金流量净额，筹资活动现金流量净额
    operating_cash_flow = [cash_flow_statement[i]['经营活动产生的现金流量净额'] for i in range(len(balance_sheet))]
    investing_cash_flow = [cash_flow_statement[i]['投资活动产生的现金流量净额'] for i in range(len(balance_sheet))]
    financing_cash_flow = [cash_flow_statement[i]['筹资活动产生的现金流量净额'] for i in range(len(balance_sheet))]
    
    
    log.debug(f"cal pe")
    # 根据股价和EPS计算的市盈率TTM（PE_TTM），市净率（PB）
    pe = [round(_calc_ratio(current_price, income_statement[i]['基本每股收益']),2) for i in range(len(income_statement))]
    fiscal_end_date = [datetime.fromtimestamp(income_statement[i]['报告日']/1000).strftime("%Y-%m-%d") for i in range(len(income_statement))]
    log.debug(f"cal fiscal end date")
    return {
        "fiscal_end_date": fiscal_end_date,
        "revenue_growth": revenue_growth,
        "gross_margin": gross_margin,
        "management_expense_ratio": management_expense_ratio,
        "sale_expense_ratio": sale_expense_ratio,
        "operating_expense_ratio": operating_expense_ratio,
        "dev_expense_ratio": dev_expense_ratio,
        "financial_cost_ratio": fin_cost_ratio,
        "total_expense_ratio": total_expense_ratio,
        "fixed_assets_ratio": fixed_assets_ratio,
        "current_assets_ratio": current_assets_ratio,
        "current_liabilities_ratio": current_liabilities_ratio,
        "long_liabilities_ratio": long_liabilities_ratio,
        "asset_turnover_ratio": asset_turnover_ratio,
        "inventory_turnover_ratio": inventory_turnover_ratio,
        "receivables_turnover_ratio": receivables_turnover_ratio,
        "payables_turnover_ratio": payables_turnover_ratio,
        "interest_coverage_ratio": interest_coverage_ratio,
        "free_cash_flow": free_cash_flow,
        "free_cash_flow_growth": free_cash_flow_growth,
        "free_cash_flow_ratio": free_cash_flow_ratio,
        "net_margin_ratio": net_margin_ratio,
        "asset_turnover_ratio": asset_turnover_ratio,
        "equity_multiplier": equity_multiplier,
        "roe": roe,
        "operating_cash_flow": operating_cash_flow,
        "investing_cash_flow": investing_cash_flow,
        "financing_cash_flow": financing_cash_flow,
        "asset_debt_ratio": asset_debt_ratio,
        "current_ratio": current_ratio,
        "quick_ratio": quick_ratio,
        "pe": pe
    }
    
def _calc_fin_hk_ratio(balance_sheet: dict, 
                    income_statement: dict, 
                    cash_flow_statement: dict, 
                    current_price:float):
    """
    计算财务指标
    Args:
        balance_sheet (dict): 资产负债表
        income_statement (dict): 利润表
        cash_flow_statement (dict): 现金流量表
        current_price (float): 当前股价
    Returns:
        dict: 财务指标
    """
    balance_sheet = json.loads(balance_sheet)
    income_statement = json.loads(income_statement)
    cash_flow_statement = json.loads(cash_flow_statement)
    balance_sheet.sort(key=lambda x: x['report_time'], reverse=True)
    income_statement.sort(key=lambda x: x['report_time'], reverse=True)
    cash_flow_statement.sort(key=lambda x: x['report_time'], reverse=True)
    log.info(f"cal revenue growth {income_statement}")
    revenue_growth = [_calc_growth_rate(income_statement[i]['营业额'], income_statement[i+1]['营业额']) for i in range(len(income_statement)-1)]
    log.debug(f"cal gross margin")
    gross_margin = [1-_calc_ratio(income_statement[i]['毛利'], income_statement[i]['营运收入']) for i in range(len(income_statement))]
    # 销售费用率，管理费用率，研发费用率，财务费用率
    log.debug(f"cal sale expense ratio")
    sale_expense_ratio = [_calc_ratio(income_statement[i]['销售及分销费用'], income_statement[i]['营运收入']) for i in range(len(income_statement))]
    log.debug(f"cal management expense ratio")
    management_expense_ratio = [_calc_ratio(income_statement[i]['行政开支'], income_statement[i]['营运收入']) for i in range(len(income_statement))]
    #log.debug(f"cal dev expense ratio")
    #dev_expense_ratio = [_calc_ratio(income_statement[i]['研发开支'], income_statement[i]['营运收入']) for i in range(len(income_statement))]
    log.debug(f"cal financial cost ratio")
    financial_cost_ratio = [_calc_ratio(income_statement[i]['融资成本'], income_statement[i]['营运收入']) for i in range(len(income_statement))]
    total_expense_ratio = [_calc_ratio(income_statement[i]['融资成本']+income_statement[i]['销售及分销费用']+income_statement[i]['行政开支'], income_statement[i]['营运收入']) for i in range(len(income_statement))]
    log.debug(f"cal fixed assets ratio")
    # 计算资产负债表的财务比率
    fixed_assets_ratio = [_calc_ratio(balance_sheet[i]['物业厂房及设备'] + balance_sheet[i]['土地使用权'], balance_sheet[i]['总资产']) for i in range(len(balance_sheet))]
    log.debug(f"cal current assets ratio")
    current_assets_ratio = [_calc_ratio(balance_sheet[i]['流动资产合计'], balance_sheet[i]['总资产']) for i in range(len(balance_sheet))]
    log.debug(f"cal current liabilities ratio")
    current_liabilities_ratio = [_calc_ratio(balance_sheet[i]['流动负债合计'], balance_sheet[i]['总资产']) for i in range(len(balance_sheet))]
    log.debug(f"cal long liabilities ratio")
    long_liabilities_ratio = [_calc_ratio(balance_sheet[i]['非流动负债合计'], balance_sheet[i]['总资产']) for i in range(len(balance_sheet))]
    
    # 资产周转率，存货周转率，应收账款周转率，应付账款周转率，利息覆盖率=ebit/利息支出
    log.debug(f"cal asset turnover ratio")
    asset_turnover_ratio = [_calc_ratio(income_statement[i]['营运收入'], balance_sheet[i]['总资产']) for i in range(len(balance_sheet))]
    log.debug(f"cal inventory turnover ratio")
    inventory_turnover_ratio = [_calc_ratio(income_statement[i]['营运收入'], balance_sheet[i]['存货']) for i in range(len(balance_sheet))]
    log.debug(f"cal receivables turnover ratio, {balance_sheet}")
    receivables_turnover_ratio = [_calc_ratio(income_statement[i]['营运收入'], balance_sheet[i]['应收帐款']) for i in range(len(balance_sheet))]
    log.debug(f"cal payables turnover ratio")
    payables_turnover_ratio = [_calc_ratio(income_statement[i]['营运收入'], balance_sheet[i]['应付帐款']) for i in range(len(balance_sheet))]
    log.debug(f"cal interest coverage ratio")
    interest_coverage_ratio = [_calc_ratio_with_keys(income_statement[i], "经营溢利", cash_flow_statement[i],"已付利息(融资)") for i in range(len(balance_sheet))]
    #[_calc_ratio(income_statement[i]['经营溢利'], cash_flow_statement[i]['已付利息(融资)']) for i in range(len(balance_sheet))]
    
    # 自由现金流，自由现金流变化率，自由现金流占销售收入的比值  
    log.debug(f"cal free cash flow: {cash_flow_statement}")
    free_cash_flow = []
    for i in range(len(cash_flow_statement)):
        if '购建固定资产' in cash_flow_statement[i].keys():
            free_cash_flow.append(cash_flow_statement[i]['经营业务现金净额'] - cash_flow_statement[i]['购建固定资产'])
        else:
            free_cash_flow.append(cash_flow_statement[i]['经营业务现金净额'])
    free_cash_flow_growth = [_calc_growth_rate(free_cash_flow[i], free_cash_flow[i+1]) for i in range(len(free_cash_flow)-1)]
    free_cash_flow_ratio = [_calc_ratio(free_cash_flow[i], income_statement[i]['营运收入']) for i in range(len(free_cash_flow))]
    log.debug(f"cal net margin ratio")
    # ROE（包括净利润率=Net Income/Revenue，总资产周转率=Revenue/Avg Assets， 权益乘数=Avg Assets / Avg Shareholder Equity）
    net_margin_ratio = [_calc_ratio(income_statement[i]['持续经营业务税后利润'], income_statement[i]['营运收入']) for i in range(len(income_statement))]
    log.debug(f"cal asset turnover ratio")
    asset_turnover_ratio = [_calc_ratio(income_statement[i]['营运收入'], balance_sheet[i]['总资产']) for i in range(len(balance_sheet))]
    log.debug(f"cal equity multiplier")
    equity_multiplier = [_calc_ratio(balance_sheet[i]['总资产'], balance_sheet[i]['总权益']) for i in range(len(balance_sheet))]
    roe = [round(net_margin_ratio[i]*asset_turnover_ratio[i]*equity_multiplier[i],2) for i in range(len(balance_sheet))]
    log.debug(f"cal asset debt ratio")
    # 资产负债率，流动比率，速动比率
    asset_debt_ratio = [_calc_ratio(balance_sheet[i]['总负债'], balance_sheet[i]['总资产']) for i in range(len(balance_sheet))]
    current_ratio = [_calc_ratio(balance_sheet[i]['流动资产合计'], balance_sheet[i]['总负债']) for i in range(len(balance_sheet))]
    quick_ratio = [_calc_ratio(balance_sheet[i]['流动资产合计'], balance_sheet[i]['流动负债合计']) for i in range(len(balance_sheet))]
    # 经营活动现金流量净额，投资活动现金流量净额，筹资活动现金流量净额
    operating_cash_flow = [cash_flow_statement[i]['经营业务现金净额'] for i in range(len(balance_sheet))]
    investing_cash_flow = [cash_flow_statement[i]['投资业务现金净额'] for i in range(len(balance_sheet))]
    financing_cash_flow = [cash_flow_statement[i]['融资业务现金净额'] for i in range(len(balance_sheet))]
    
    log.debug(f"cal pe")
    # 根据股价和EPS计算的市盈率TTM（PE_TTM），市净率（PB）
    pe = [round(_calc_ratio(current_price, income_statement[i]['每股基本盈利']),2) for i in range(len(income_statement))]
    fiscal_end_date = [income_statement[i]['report_time'] for i in range(len(income_statement))]
    log.debug(f"cal fiscal end date: {fiscal_end_date}")
    return {
        "fiscal_end_date": fiscal_end_date,
        "revenue_growth": revenue_growth,
        "gross_margin": gross_margin,
        "sale_expense_ratio": sale_expense_ratio,
        "management_expense_ratio": management_expense_ratio,
        "financial_cost_ratio": financial_cost_ratio,
        "total_expense_ratio": total_expense_ratio,
        "fixed_assets_ratio": fixed_assets_ratio,
        "current_assets_ratio": current_assets_ratio,
        "current_liabilities_ratio": current_liabilities_ratio,
        "long_liabilities_ratio": long_liabilities_ratio,
        "asset_turnover_ratio": asset_turnover_ratio,
        "inventory_turnover_ratio": inventory_turnover_ratio,
        "receivables_turnover_ratio": receivables_turnover_ratio,
        "payables_turnover_ratio": payables_turnover_ratio,
        "interest_coverage_ratio": interest_coverage_ratio,
        "free_cash_flow": free_cash_flow,
        "free_cash_flow_growth": free_cash_flow_growth,
        "free_cash_flow_ratio": free_cash_flow_ratio,
        "operating_cash_flow": operating_cash_flow,
        "investing_cash_flow": investing_cash_flow,
        "financing_cash_flow": financing_cash_flow,
        "net_margin_ratio": net_margin_ratio,
        "asset_turnover_ratio": asset_turnover_ratio,
        "equity_multiplier": equity_multiplier,
        "roe": roe,
        "asset_debt_ratio": asset_debt_ratio,
        "current_ratio": current_ratio,
        "quick_ratio": quick_ratio,
        "pe": pe
    }
    
    
    
    
    
    
    
    
    