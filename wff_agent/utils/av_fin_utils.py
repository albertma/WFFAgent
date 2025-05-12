# -*- coding: utf-8 -*-
import logging
from . import fcf_valuation
from . import agent_utils

log = logging.getLogger(__name__)
def _growth_rate(current: str, previous: str) -> dict:
    """计算增长率"""
    if current == "None" or previous == "None":
        return 0.0
    elif int(previous) == 0:
        return 0.0
    else:
        return round((int(current) - int(previous)) / int(previous),4)

def _calculate_ratios(share:str, total:str) -> dict:
    """计算比率"""
    if share == "None" or total == "None": 
        return 0.0
    elif int(total) == 0:
        return 0.0
    else:
        return round(int(share) / int(total), 4)

def _substract(a: str, b: str) -> dict:
    """计算差值"""
    if a == "None" or b == "None":
        return 0.0
    else:
        return int(a) - int(b)

def calc_us_indicators(data: dict, stock_price:float = 100, discount_rate:float=0.09, growth_rate:float=0.01) -> dict:
    log.info("calc_us_indicators")
    annual_balance_sheet = data["balance_sheet"]["annualReports"]
    annual_income_statement = data["income_statement"]["annualReports"]
    annual_cashflow_statement = data["cashflow"]["annualReports"]
    # 计算财务指标
    log.info("开始计算财务指标: annualReports")
    # 计算经营活动现金流量净额，投资活动现金流量净额，筹资活动现金流量净额

    annual_indicators = _calculate_financial_ratios(
        annual_balance_sheet, annual_income_statement, annual_cashflow_statement, stock_price, annual=True
    )
    quarterly_balance_sheet = data["balance_sheet"]["quarterlyReports"]
    quarterly_income_statement = data["income_statement"]["quarterlyReports"]
    quarterly_cashflow_statement = data["cashflow"]["quarterlyReports"]
    log.debug("开始计算财务指标: quarterlyReports")
    quarterly_indicators = _calculate_financial_ratios(
        quarterly_balance_sheet, quarterly_income_statement, quarterly_cashflow_statement, stock_price, annual=False
    )
    log.debug("calculate fcf valuation")
    # 计算最近3年的free cash flow平均增长率
    free_cash_flow = [
        _substract(annual_cashflow_statement[i]["operatingCashflow"], annual_cashflow_statement[i]["capitalExpenditures"])
        for i in range(len(annual_cashflow_statement))
    ]
    free_cash_flow_growth = [
        _growth_rate(free_cash_flow[i], free_cash_flow[i + 1])
        for i in range(len(free_cash_flow) - 1)
    ]
    average_growth_rate = round(sum(free_cash_flow_growth) / len(free_cash_flow_growth),2)
    log.debug(f"Average_growth_rate: {average_growth_rate}")
    # 根据最近3年的free cash flow平均增长率计算未来5年的自由现金流
    # 计算未来5年的自由现金流折现值
    # discount_rate = 0.1  # 假设折现率为10%
    # growth_rate = 0.05  # 假设长期增长率为5%
    shares_num = annual_balance_sheet[0]["commonStockSharesOutstanding"]
    log.debug(f"shares_num: {shares_num}")
    
    fcf_valuation_result = fcf_valuation.free_cash_flow_valuation(
        latest_fcf=free_cash_flow[0],
        recent_3_yr_fcf_avg_growth=average_growth_rate,
        discount_rate=discount_rate,
        growth_rate=growth_rate,
        shares_num=shares_num
    )
    
    return {
        "annual": annual_indicators,
        "quarterly": quarterly_indicators,
        "fcf_valuation": fcf_valuation_result,
    }

def _calculate_financial_ratios(balance_sheet:list, income_statement:list, cashflow_statement:list, stock_price:float, annual:bool) -> dict:
    """计算财务比率"""
    length = min(len(balance_sheet), len(income_statement))
    length = min(length, len(cashflow_statement))
    if annual:
        length = min(6, length)
    else:
        length = min(6, length)
    # 计算财务指标
    log.debug(f"calc revenue growth")
    balance_sheet.sort(key=lambda x: x["fiscalDateEnding"], reverse=True)
    income_statement.sort(key=lambda x: x["fiscalDateEnding"], reverse=True)
    cashflow_statement.sort(key=lambda x: x["fiscalDateEnding"], reverse=True)
    print(f"income_statement: {income_statement}")
    revenue_growth = [_growth_rate(income_statement[i]["totalRevenue"], income_statement[i+1]["totalRevenue"]) for i in range(length)]
    gross_margin = [_calculate_ratios(income_statement[i]["grossProfit"], income_statement[i]["totalRevenue"]) for i in range(length)]
    
    log.debug(f"data length: {length}")
    # 计算各项费用比率
    log.debug(f"calc expenses ratio")
    operating_expenses_ratio = [_calculate_ratios(income_statement[i]["operatingExpenses"], income_statement[i]["totalRevenue"]) for i in range(length)]
    selling_expenses_ratio = [_calculate_ratios(income_statement[i]["sellingGeneralAndAdministrative"], income_statement[i]["totalRevenue"]) for i in range(length)]
    r_and_d_expenses_ratio = [_calculate_ratios(income_statement[i]["researchAndDevelopment"], income_statement[i]["totalRevenue"]) for i in range(length)]
    interest_expenses_ratio = [_calculate_ratios(income_statement[i]["interestExpense"], income_statement[i]["totalRevenue"]) for i in range(length)]
    total_expenses_ratio = [operating_expenses_ratio[i]+ selling_expenses_ratio[i] + r_and_d_expenses_ratio[i] + interest_expenses_ratio[i] for i in range(length)]

    # 固定资产占比，流动资产占比，流动负债占比，长期负债占比
    log.debug(f"calc assets ratio")
    fixed_assets_ratio = [_calculate_ratios(balance_sheet[i]["propertyPlantEquipment"], balance_sheet[i]["totalAssets"]) for i in range(length)]
    current_assets_ratio = [_calculate_ratios(balance_sheet[i]["totalCurrentAssets"], balance_sheet[i]["totalAssets"]) for i in range(length)]
    current_liabilities_ratio = [_calculate_ratios(balance_sheet[i]["totalCurrentLiabilities"], balance_sheet[i]["totalLiabilities"]) for i in range(length)]
    long_term_liabilities_ratio = [_calculate_ratios(balance_sheet[i]["totalNonCurrentLiabilities"], balance_sheet[i]["totalLiabilities"]) for i in range(length)]
    
    # 资产周转率，存货周转率，应收账款周转率，应付账款周转率，利息覆盖率=ebit/利息支出
    log.debug(f"calc turnover ratio")
    asset_turnover_ratio = [_calculate_ratios(income_statement[i]["totalRevenue"], balance_sheet[i]["totalAssets"]) for i in range(length)]
    inventory_turnover_ratio = [_calculate_ratios(income_statement[i]["costOfRevenue"], balance_sheet[i]["inventory"]) for i in range(length)]
    receivables_turnover_ratio = [_calculate_ratios(income_statement[i]["totalRevenue"], balance_sheet[i]["currentNetReceivables"]) for i in range(length)]
    payables_turnover_ratio = [_calculate_ratios(income_statement[i]["costOfRevenue"], balance_sheet[i]["currentAccountsPayable"]) for i in range(length)]
    interest_coverage_ratio = [_calculate_ratios(income_statement[i]["ebit"], income_statement[i]["interestExpense"]) for i in range(length)]
    
    # 自由现金流，自由现金流变化率，自由现金流占销售收入的比值
    log.debug(f"calc free cashflow ratio")
    free_cash_flow = [ _substract(cashflow_statement[i]["operatingCashflow"],cashflow_statement[i]["capitalExpenditures"]) for i in range(length)]
    free_cash_flow_change_rate = [_growth_rate(free_cash_flow[i], free_cash_flow[i+1]) for i in range(length-1)]
    free_cash_flow_ratio = [_calculate_ratios(free_cash_flow[i], income_statement[i]["totalRevenue"]) for i in range(length-1)]
    # ROE（包括净利润率=Net Income/Revenue，总资产周转率=Revenue/Avg Assets， 权益乘数=Avg Assets / Avg Shareholder Equity）
    log.debug(f"calc roe")
    net_income_margin = [_calculate_ratios(income_statement[i]["netIncome"], income_statement[i]["totalRevenue"]) for i in range(length)]
    total_asset_turnover = [_calculate_ratios(income_statement[i]["totalRevenue"], (int(balance_sheet[i]["totalAssets"]) + int(balance_sheet[i+1]["totalAssets"])) / 2) for i in range(length)]
    equity_multiplier = [_calculate_ratios((int(balance_sheet[i]["totalAssets"]) + int(balance_sheet[i+1]["totalAssets"])) / 2, (int(balance_sheet[i]["totalShareholderEquity"]) + int(balance_sheet[i+1]["totalShareholderEquity"])) / 2) for i in range(length)]
    roe = [round(net_income_margin[i] * total_asset_turnover[i] * equity_multiplier[i],2) for i in range(length)]
    
        
    # 资产负债率，流动比率，速动比率
    log.debug(f"calc debt ratio")
    debt_ratio = [_calculate_ratios(balance_sheet[i]["totalLiabilities"], balance_sheet[i]["totalAssets"]) for i in range(length)]
    current_ratio = _calculate_ratios(balance_sheet[0]["totalCurrentAssets"], balance_sheet[0]["totalCurrentLiabilities"])
    quick_ratio = _calculate_ratios(
        _substract(balance_sheet[0]["totalCurrentAssets"], balance_sheet[0]["inventory"]),
        balance_sheet[0]["totalCurrentLiabilities"]
    )
    
    # 计算经营活动现金流量净额，投资活动现金流量净额，筹资活动现金流量净额
    log.debug(f"calc operating cash flow:{cashflow_statement}")
    operating_cash_flow = [cashflow_statement[i]["operatingCashflow"] for i in range(length)]
    investing_cash_flow = [cashflow_statement[i]["cashflowFromInvestment"] for i in range(length)]
    financing_cash_flow = [cashflow_statement[i]["cashflowFromFinancing"] for i in range(length)]
    # 根据股价和EPS计算的市盈率TTM（PE_TTM），市净率（PB）
    log.debug(f"calc pe pb ratio")
    if annual:
       
        earnings_per_share = [_calculate_ratios(income_statement[i]["netIncome"], balance_sheet[i]["commonStockSharesOutstanding"]) for i in range(length)]
        booking_value_per_share = [_calculate_ratios(balance_sheet[i]["totalShareholderEquity"], balance_sheet[i]["commonStockSharesOutstanding"]) for i in range(length)]
        pe_ratio_ttm = _calculate_ratios(stock_price, earnings_per_share[0])
        pb_ratio = _calculate_ratios(stock_price, booking_value_per_share[0])
    else:
        pe_ratio_ttm = 0
        pb_ratio = 0
    
    fiscal_ending_dates = [
        balance_sheet[i]["fiscalDateEnding"] for i in range(length)
    ]
   
    return {
        "fiscalDateEnding": fiscal_ending_dates,
        "revenue_growth": revenue_growth,
        "gross_margin": gross_margin,
        "operating_expenses_ratio": operating_expenses_ratio,
        "selling_expenses_ratio": selling_expenses_ratio,
        "r_and_d_expenses_ratio": r_and_d_expenses_ratio,
        "interest_expenses_ratio": interest_expenses_ratio,
        "total_expenses_ratio": total_expenses_ratio,
        "fixed_assets_ratio": fixed_assets_ratio,
        "current_assets_ratio": current_assets_ratio,
        "current_liabilities_ratio": current_liabilities_ratio,
        "long_term_liabilities_ratio": long_term_liabilities_ratio,
        "asset_turnover_ratio": asset_turnover_ratio,
        "inventory_turnover_ratio": inventory_turnover_ratio,
        "receivables_turnover_ratio": receivables_turnover_ratio,
        "payables_turnover_ratio": payables_turnover_ratio,
        "interest_coverage_ratio": interest_coverage_ratio,
        "free_cash_flow": free_cash_flow,
        "free_cash_flow_change_rate": free_cash_flow_change_rate,
        "free_cash_flow_ratio": free_cash_flow_ratio,
        "net_income_margin": net_income_margin,
        "total_asset_turnover": total_asset_turnover,
        "equity_multiplier": equity_multiplier,
        "roe": roe,
        "debt_ratio": debt_ratio,
        "current_ratio": current_ratio,
        "quick_ratio": quick_ratio,
        "operating_cash_flow": operating_cash_flow,
        "investing_cash_flow": investing_cash_flow,
        "financing_cash_flow": financing_cash_flow,
        "pe_ttm": pe_ratio_ttm,
        "pb_ttm": pb_ratio,
    }
    
if __name__ == '__main__':
    balance_sheet = agent_utils.read_json(r"./AAPL&BALANCE_SHEET.json")
    income_statement = agent_utils.read_json(r"./AAPL&INCOME_STATEMENT.json")
    cashflow = agent_utils.read_json(r"./AAPL&CASH_FLOW.json")
    reports =  {
        "balanceSheet": balance_sheet, 
        "incomeStatement": income_statement,
        "cashflow": cashflow
        }
    result = calc_us_indicators(reports, 206)
    print(result)