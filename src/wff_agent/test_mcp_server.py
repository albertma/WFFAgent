import asyncio
import logging
from .mcp_server import (
    GetMarketIndicators,
    GetLatestStockPrice,
    AnalyzeFinancials,
    get_management_discussion,
    check_valid_symbol
)

# 设置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

async def test_get_market_indicators():
    """测试获取市场指标"""
    try:
        log.info("测试获取市场指标")
        result = await GetMarketIndicators("AAPL", "us")
        log.info(f"市场指标结果: {result}")
    except Exception as e:
        log.error(f"测试失败: {str(e)}", exc_info=True)

async def test_get_latest_stock_price():
    """测试获取最新股票价格"""
    try:
        log.info("测试获取最新股票价格")
        result = await GetLatestStockPrice("AAPL", "us")
        log.info(f"股票价格结果: {result}")
    except Exception as e:
        log.error(f"测试失败: {str(e)}", exc_info=True)

async def test_analyze_financials():
    """测试分析财务指标"""
    try:
        log.info("测试分析财务指标")
        result = await AnalyzeFinancials(
            symbol="AAPL",
            market="us",
            stock_price=150.0,
            discount_rate=0.06,
            growth_rate=0.02,
            total_shares=1000000
        )
        log.info(f"财务分析结果: {result}")
    except Exception as e:
        log.error(f"测试失败: {str(e)}", exc_info=True)

async def test_get_management_discussion():
    """测试获取管理层讨论"""
    try:
        log.info("测试获取管理层讨论")
        result = await get_management_discussion("AAPL", "us")
        log.info(f"管理层讨论结果: {result}")
    except Exception as e:
        log.error(f"测试失败: {str(e)}", exc_info=True)

async def test_check_valid_symbol():
    """测试检查股票代码有效性"""
    try:
        log.info("测试检查股票代码有效性")
        result = await check_valid_symbol("AAPL", "us")
        log.info(f"股票代码有效性结果: {result}")
    except Exception as e:
        log.error(f"测试失败: {str(e)}", exc_info=True)

async def run_all_tests():
    """运行所有测试"""
    log.info("开始运行所有测试")
    
    # 测试检查股票代码有效性
   # await test_check_valid_symbol()
    
    # 测试获取最新股票价格
    #await test_get_latest_stock_price()
    
    # 测试获取市场指标
    await test_get_market_indicators()
    
    # 测试分析财务指标
    #await test_analyze_financials()
    
    # 测试获取管理层讨论
    #await test_get_management_discussion()
    
    log.info("所有测试完成")

if __name__ == "__main__":
    asyncio.run(run_all_tests()) 