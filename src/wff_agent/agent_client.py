# 标准库导入
import asyncio
from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler

from typing import Dict, Any, Callable, Optional

# 本地应用导入
from wff_agent.agent_factory import AgentFactory
from wff_agent.stock_analysis_workflow import StockAnalysisWorkflow
from wff_agent.utils.stock_utils import is_valid_symbol
# 配置日志
log_file = 'wff_agent.log'
handler = TimedRotatingFileHandler(
    log_file, when='midnight', interval=1, backupCount=7, encoding='utf-8'
)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
log.addHandler(handler)
# 环境变量
async def run_crypto_agent(symbol: str, progress_callback: Optional[Callable] = None):
    """运行加密货币 agent
    
    Args:
        symbol (str): 加密货币代码
        progress_callback (Optional[Callable]): 进度回调函数
    Returns:
        Dict[str, Any]: 分析结果
    """
    pass
    

async def run_stock_agent(symbol: str, market: str, discount_rate: float, 
                    growth_rate: float, total_shares: int=0, agent_names: list=[],
                    progress_callback: Optional[Callable] = None):
    """运行 agent
    
    Args:
        symbol (str): 股票代码
        market (str): 市场代码
        discount_rate (float): 折现率
        growth_rate (float): 增长率
        total_shares (int): 总股本
        agent_names (list): 要执行的 agent 名称列表
    Returns:
        Dict[str, Any]: 分析结果
    """
    if len(agent_names) == 0 or agent_names is None:
        agent_names = ["NewsAnalysisAgent", 
                       "TechAnalysisAgent", 
                       "FundamentalAnalysisAgent", 
                       "GlobalMarketAnalysisAgent", 
                       "ComprehensiveAnalysisAgent"]
    log.info(f"agent_names: {agent_names}")
    agents = []
    for agent_name in agent_names:
        try:
            agent = AgentFactory.instance().create_agent(agent_name)
            agents.append(agent)
        except Exception as e:
            log.error(f"Agent {agent_name} 创建失败: {str(e)}", exc_info=True)
            continue
       
    try:
       
        workflow = StockAnalysisWorkflow(
            agents=agents,
            progress_callback=progress_callback
        )
        date_str = datetime.now().strftime("%Y-%m-%d")
        result = await workflow.execute(input_data={
                "symbol":symbol, 
                "market":market, 
                "discount_rate":discount_rate, 
                "growth_rate":growth_rate, 
                "total_shares":total_shares,
                "date":date_str
                })
        log.info(f"Agent Flow result: {result}")
        return result
        
    except Exception as e:
        log.error(f"Agent 执行失败: {str(e)}", exc_info=True)
        raise

async def main(symbol: str, market: str, discount_rate: float, growth_rate: float, total_shares: int=0, agent_names: list=[], progress_callback: Optional[Callable] = None):
    """主函数"""
    # 检查股票代码有效性
    if not is_valid_symbol(symbol, market):
        log.error(f"股票代码无效: {symbol}, {market}")
        raise ValueError(f"股票代码无效: {symbol}, {market}")
    
    try:
        log.info(f"开始执行 Agent 分析: {symbol}, {market}, {discount_rate}, {growth_rate}, {total_shares}")
        result = await run_stock_agent(symbol, market, discount_rate, growth_rate, total_shares, agent_names, progress_callback)
        log.info(f"Agent 执行结果: \n{result}")
        return result
    except Exception as e:
        log.error(f"""
        [ERROR] Agent 执行失败:
        - 类型: {type(e).__name__}
        - 消息: {str(e)}
        - 文件: {e.__traceback__.tb_frame.f_code.co_filename}
        - 行号: {e.__traceback__.tb_lineno}
        """, exc_info=True)

