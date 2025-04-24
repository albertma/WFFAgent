
# -*- coding: utf-8 -*-
import logging
logging.basicConfig(level=logging.DEBUG)

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

def _divide(a: str, b: str) -> dict:
    """计算除法"""
    if a == "None" or b == "None":
        return 0.0
    elif int(b) == 0:
        return 0.0
    else:
        return round(int(a) / int(b), 4)
# 解析财报数据
# 这里假设数据已经被解析为字典格式
# 例如：
"""
data =  
    {
        "balanceSheet":{
        "symbol": "AAPL",
        "annualReports": [
        {
            "fiscalDateEnding": "2024-09-30",
            "reportedCurrency": "USD",
            "totalAssets": "364980000000",
            "totalCurrentAssets": "152987000000",
            "cashAndCashEquivalentsAtCarryingValue": "29943000000",
            "cashAndShortTermInvestments": "65171000000",
            "inventory": "7286000000",
            "currentNetReceivables": "66243000000",
            "totalNonCurrentAssets": "211993000000",
            "propertyPlantEquipment": "45680000000",
            "accumulatedDepreciationAmortizationPPE": "73448000000",
            "intangibleAssets": "None",
            "intangibleAssetsExcludingGoodwill": "None",
            "goodwill": "None",
            "investments": "254763000000",
            "longTermInvestments": "91479000000",
            "shortTermInvestments": "35228000000",
            "otherCurrentAssets": "14287000000",
            "otherNonCurrentAssets": "74834000000",
            "totalLiabilities": "308030000000",
            "totalCurrentLiabilities": "176392000000",
            "currentAccountsPayable": "68960000000",
            "deferredRevenue": "21049000000",
            "currentDebt": "21023000000",
            "shortTermDebt": "9967000000",
            "totalNonCurrentLiabilities": "131638000000",
            "capitalLeaseObligations": "752000000",
            "longTermDebt": "96662000000",
            "currentLongTermDebt": "10912000000",
            "longTermDebtNoncurrent": "85750000000",
            "shortLongTermDebtTotal": "106629000000",
            "otherCurrentLiabilities": "78304000000",
            "otherNonCurrentLiabilities": "45888000000",
            "totalShareholderEquity": "56950000000",
            "treasuryStock": "None",
            "retainedEarnings": "-19154000000",
            "commonStock": "83276000000",
            "commonStockSharesOutstanding": "15116786000"
        }],
        "quarterlyReports": []
    },
    "incomeStatement": {
        "symbol": "AAPL",
        "annualReports": [
        {
            "fiscalDateEnding": "2024-09-30",
            "reportedCurrency": "USD",
            "grossProfit": "180683000000",
            "totalRevenue": "391035000000",
            "costOfRevenue": "236449000000",
            "costofGoodsAndServicesSold": "210352000000",
            "operatingIncome": "123216000000",
            "sellingGeneralAndAdministrative": "26097000000",
            "researchAndDevelopment": "31370000000",
            "operatingExpenses": "57467000000",
            "investmentIncomeNet": "None",
            "netInterestIncome": "None",
            "interestIncome": "None",
            "interestExpense": "None",
            "nonInterestIncome": "391035000000",
            "otherNonOperatingIncome": "None",
            "depreciation": "8200000000",
            "depreciationAndAmortization": "11445000000",
            "incomeBeforeTax": "123485000000",
            "incomeTaxExpense": "29749000000",
            "interestAndDebtExpense": "None",
            "netIncomeFromContinuingOperations": "93736000000",
            "comprehensiveIncomeNetOfTax": "98016000000",
            "ebit": "123216000000",
            "ebitda": "134661000000",
            "netIncome": "93736000000"
        }],
        "quarterlyReports": []
    },
    "cashflow": {
        "symbol": "AAPL",
        "annualReports": [
        {
            "fiscalDateEnding": "2024-09-30",
            "reportedCurrency": "USD",
            "operatingCashflow": "118254000000",
            "paymentsForOperatingActivities": "1900000000",
            "proceedsFromOperatingActivities": "None",
            "changeInOperatingLiabilities": "21572000000",
            "changeInOperatingAssets": "17921000000",
            "depreciationDepletionAndAmortization": "11445000000",
            "capitalExpenditures": "9447000000",
            "changeInReceivables": "5144000000",
            "changeInInventory": "1046000000",
            "profitLoss": "93736000000",
            "cashflowFromInvestment": "2935000000",
            "cashflowFromFinancing": "-121983000000",
            "proceedsFromRepaymentsOfShortTermDebt": "7920000000",
            "paymentsForRepurchaseOfCommonStock": "94949000000",
            "paymentsForRepurchaseOfEquity": "94949000000",
            "paymentsForRepurchaseOfPreferredStock": "None",
            "dividendPayout": "15234000000",
            "dividendPayoutCommonStock": "15234000000",
            "dividendPayoutPreferredStock": "None",
            "proceedsFromIssuanceOfCommonStock": "None",
            "proceedsFromIssuanceOfLongTermDebtAndCapitalSecuritiesNet": "0",
            "proceedsFromIssuanceOfPreferredStock": "None",
            "proceedsFromRepurchaseOfEquity": "-94949000000",
            "proceedsFromSaleOfTreasuryStock": "None",
            "changeInCashAndCashEquivalents": "None",
            "changeInExchangeRate": "None",
            "netIncome": "93736000000"
        }],
        "quarterlyReports": []
      }
    }
"""  
def calculate_financial_indicators(data: dict, stock_price:float, discount_rate:float=0.06, growth_rate:float=0.02) -> dict:
    logging.debug("calculate_financial_indicators")
    annual_balance_sheet = data["balanceSheet"]["annualReports"]
    annual_income_statement = data["incomeStatement"]["annualReports"]
    annual_cashflow_statement = data["cashflow"]["annualReports"]
    # 计算财务指标
    logging.debug("开始计算财务指标: annualReports")
    annual_indicators = _calculate_financial_ratios(
        annual_balance_sheet, annual_income_statement, annual_cashflow_statement, stock_price, annual=True
    )
    quarterly_balance_sheet = data["balanceSheet"]["quarterlyReports"]
    quarterly_income_statement = data["incomeStatement"]["quarterlyReports"]
    quarterly_cashflow_statement = data["cashflow"]["quarterlyReports"]
    logging.debug("开始计算财务指标: quarterlyReports")
    quarterly_indicators = _calculate_financial_ratios(
        quarterly_balance_sheet, quarterly_income_statement, quarterly_cashflow_statement, stock_price, annual=False
    )
    logging.debug("calc fcf valuation")
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
    logging.debug(f"average_growth_rate: {average_growth_rate}")
    # 根据最近3年的free cash flow平均增长率计算未来5年的自由现金流
    future_free_cash_flow = []
    for i in range(5):
        if i == 0:
            future_free_cash_flow.append(free_cash_flow[0] * (1 + average_growth_rate))
        else:
            future_free_cash_flow.append(future_free_cash_flow[i - 1] * (1 + average_growth_rate))
    # 计算未来5年的自由现金流折现值
    # discount_rate = 0.1  # 假设折现率为10%
    # growth_rate = 0.05  # 假设长期增长率为5%
    shares_num = annual_balance_sheet[0]["commonStockSharesOutstanding"]
    logging.debug(f"shares_num: {shares_num}")
    intrinsic_value = _fcf_valuation(future_free_cash_flow, discount_rate, growth_rate, shares_num)
    # 将计算结果添加到annual_indicators和quarterly_indicators中
    fcf_valuation_result = {
        "intrinsic_value": intrinsic_value,
        "future_free_cash_flow": future_free_cash_flow,
        "average_growth_rate": average_growth_rate,
        "discount_rate": discount_rate,
        "growth_rate": growth_rate,
        "shares_num": shares_num,
    
    }
    return {
        "annual": annual_indicators,
        "quarterly": quarterly_indicators,
        "fcf_valuation": fcf_valuation_result,
    }
def _fcf_valuation(free_cash_flow: list, discount_rate: float, growth_rate: float, shares_num:int) -> float:
    """自由现金流折现估值"""
    if shares_num == 0 or shares_num == "None":
        print("股票数量为0")
        return 0.0
    length = len(free_cash_flow)
    if length == 0:
        print("自由现金流数据为空")
        return 0.0
    present_value = 0
    for i in range(len(free_cash_flow)):
        present_value += free_cash_flow[i] / ((1 + discount_rate) ** (i + 1))
    logging.debug(f"present_value: {present_value}")
    terminal_value = (free_cash_flow[-1] * (1 + growth_rate)) / (discount_rate - growth_rate)
    present_value += terminal_value / ((1 + discount_rate) ** len(free_cash_flow))
    intrinsic_value = present_value / int(shares_num) 
    logging.debug(f"intrinsic_value: {intrinsic_value}")
    return intrinsic_value

def _calculate_financial_ratios(balance_sheet:dict, income_statement:dict, cashflow_statement:dict, stock_price:float, annual:bool) -> dict:
    """计算财务比率"""
    length = min(len(balance_sheet), len(income_statement))
    length = min(length, len(cashflow_statement))
    if annual:
        length = min(5, length)
    else:
        length = min(6, length)
    # 计算财务指标
    revenue_growth = [_growth_rate(income_statement[i]["totalRevenue"], income_statement[i+1]["totalRevenue"]) for i in range(length)]
    gross_margin = [_calculate_ratios(income_statement[i]["grossProfit"], income_statement[i]["totalRevenue"]) for i in range(length)]
    
    logging.debug(f"data length: {length}")
    # 计算各项费用比率
    logging.debug(f"calc expenses ratio")
    operating_expenses_ratio:dict = [_calculate_ratios(income_statement[i]["operatingExpenses"], income_statement[i]["totalRevenue"]) for i in range(length)]
    selling_expenses_ratio:dict = [_calculate_ratios(income_statement[i]["sellingGeneralAndAdministrative"], income_statement[i]["totalRevenue"]) for i in range(length)]
    r_and_d_expenses_ratio:dict = [_calculate_ratios(income_statement[i]["researchAndDevelopment"], income_statement[i]["totalRevenue"]) for i in range(length)]
    interest_expenses_ratio:dict = [_calculate_ratios(income_statement[i]["interestExpense"], income_statement[i]["totalRevenue"]) for i in range(length)]
    total_expenses_ratio = [operating_expenses_ratio[i]+ selling_expenses_ratio[i] + r_and_d_expenses_ratio[i] + interest_expenses_ratio[i] for i in range(length)]

    # 固定资产占比，流动资产占比，流动负债占比，长期负债占比
    logging.debug(f"calc assets ratio")
    fixed_assets_ratio = [_calculate_ratios(balance_sheet[i]["propertyPlantEquipment"], balance_sheet[i]["totalAssets"]) for i in range(length)]
    current_assets_ratio = [_calculate_ratios(balance_sheet[i]["totalCurrentAssets"], balance_sheet[i]["totalAssets"]) for i in range(length)]
    current_liabilities_ratio = [_calculate_ratios(balance_sheet[i]["totalCurrentLiabilities"], balance_sheet[i]["totalLiabilities"]) for i in range(length)]
    long_term_liabilities_ratio = [_calculate_ratios(balance_sheet[i]["totalNonCurrentLiabilities"], balance_sheet[i]["totalLiabilities"]) for i in range(length)]
    
    # 资产周转率，存货周转率，应收账款周转率，应付账款周转率，利息覆盖率=ebit/利息支出
    logging.debug(f"calc turnover ratio")
    asset_turnover_ratio = [_calculate_ratios(income_statement[i]["totalRevenue"], balance_sheet[i]["totalAssets"]) for i in range(length)]
    inventory_turnover_ratio = [_calculate_ratios(income_statement[i]["costOfRevenue"], balance_sheet[i]["inventory"]) for i in range(length)]
    receivables_turnover_ratio = [_calculate_ratios(income_statement[i]["totalRevenue"], balance_sheet[i]["currentNetReceivables"]) for i in range(length)]
    payables_turnover_ratio = [_calculate_ratios(income_statement[i]["costOfRevenue"], balance_sheet[i]["currentAccountsPayable"]) for i in range(length)]
    interest_coverage_ratio = [_calculate_ratios(income_statement[i]["ebit"], income_statement[i]["interestExpense"]) for i in range(length)]
    
    # 自由现金流，自由现金流变化率，自由现金流占销售收入的比值
    logging.debug(f"calc free cashflow ratio")
    free_cash_flow = [ _substract(cashflow_statement[i]["operatingCashflow"],cashflow_statement[i]["capitalExpenditures"]) for i in range(length)]
    free_cash_flow_change_rate = [_growth_rate(free_cash_flow[i], free_cash_flow[i+1]) for i in range(length-1)]
    free_cash_flow_ratio = [_calculate_ratios(free_cash_flow[i], income_statement[i]["totalRevenue"]) for i in range(length-1)]
    # ROE（包括净利润率=Net Income/Revenue，总资产周转率=Revenue/Avg Assets， 权益乘数=Avg Assets / Avg Shareholder Equity）
    logging.debug(f"calc roe")
    net_income_margin = [_calculate_ratios(income_statement[i]["netIncome"], income_statement[i]["totalRevenue"]) for i in range(length)]
    total_asset_turnover = [_calculate_ratios(income_statement[i]["totalRevenue"], (int(balance_sheet[i]["totalAssets"]) + int(balance_sheet[i+1]["totalAssets"])) / 2) for i in range(length)]
    equity_multiplier = [_calculate_ratios((int(balance_sheet[i]["totalAssets"]) + int(balance_sheet[i+1]["totalAssets"])) / 2, (int(balance_sheet[i]["totalShareholderEquity"]) + int(balance_sheet[i+1]["totalShareholderEquity"])) / 2) for i in range(length)]
    roe = [round(net_income_margin[i] * total_asset_turnover[i] * equity_multiplier[i],2) for i in range(length)]
    
        
    # 资产负债率，流动比率，速动比率
    logging.debug(f"calc debt ratio")
    debt_ratio = [_calculate_ratios(balance_sheet[i]["totalLiabilities"], balance_sheet[i]["totalAssets"]) for i in range(length)]
    current_ratio = _divide(balance_sheet[0]["totalCurrentAssets"], balance_sheet[0]["totalCurrentLiabilities"])
    quick_ratio = _calculate_ratios(
        _substract(balance_sheet[0]["totalCurrentAssets"], balance_sheet[0]["inventory"]),
        balance_sheet[0]["totalCurrentLiabilities"]
    )
    logging.debug(f"calc pe pb ratio")
    # 根据股价和EPS计算的市盈率TTM（PE_TTM），市净率（PB）
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
        "pe_ttm": pe_ratio_ttm,
        "pb_ttm": pb_ratio,
    }
    
    