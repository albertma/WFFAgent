# 标准库导入
import asyncio
from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
import os
from typing import Dict, Any

# 本地应用导入
from wff_agent.stock_agents import ComprehensiveAnalysisAgent
from wff_agent.stock_agents import FundamentalAnalysisAgent
from wff_agent.stock_agents import TechAnalysisAgent
from wff_agent.stock_agents import NewsAnalysisAgent
from wff_agent.stock_agents import GlobalMarketAnalysisAgent
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
api_key = os.getenv("DEEPSEEK_API_KEY")

async def run_agent(symbol: str, market: str, discount_rate: float, 
                    growth_rate: float, total_shares: int=0, agent_names: list=[]):
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
        agent_names = ["NewsAnalysisAgent", "TechAnalysisAgent", 
                       "FundamentalAnalysisAgent", 
                       "GlobalMarketAnalysisAgent", "ComprehensiveAnalysisAgent"]
    log.info(f"agent_names: {agent_names}")
    agents = []
    for agent_name in agent_names:
        if agent_name == "NewsAnalysisAgent":
            agent = NewsAnalysisAgent(
                base_url=os.getenv("DEEPSEEK_BASE_URL"),
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                model= "deepseek-chat",
                temperature= 0.3,
                max_tokens=64096)
        elif agent_name == "TechAnalysisAgent":
            agent = TechAnalysisAgent(
                base_url=os.getenv("DEEPSEEK_BASE_URL"),
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                model= "deepseek-chat",
                temperature= 0.3,
                max_tokens=64096)
        elif agent_name == "FundamentalAnalysisAgent":
            agent = FundamentalAnalysisAgent(
                base_url=os.getenv("DEEPSEEK_BASE_URL"),
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                model= "deepseek-chat",
                temperature= 0.3,
                max_tokens=64096)
        elif agent_name == "GlobalMarketAnalysisAgent":
            agent = GlobalMarketAnalysisAgent(
                base_url=os.getenv("DEEPSEEK_BASE_URL"),
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                model= "deepseek-chat",
                temperature= 0.3,
                max_tokens=64096)
        elif agent_name == "ComprehensiveAnalysisAgent":
            agent = ComprehensiveAnalysisAgent(
                base_url=os.getenv("DEEPSEEK_BASE_URL"),
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                model= "deepseek-chat",
                temperature= 0.1,
                max_tokens=64096)
        else:
            log.warning(f"Invalid agent name: {agent_name}")
            continue
        agents.append(agent)
    try:
       
        workflow = StockAnalysisWorkflow(
            agents=agents
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

async def main(symbol: str, market: str, discount_rate: float, growth_rate: float, total_shares: int=0, agent_names: list=[]):
    """主函数"""
    # 检查股票代码有效性
    if not is_valid_symbol(symbol, market):
        log.error(f"股票代码无效: {symbol}, {market}")
        raise ValueError(f"股票代码无效: {symbol}, {market}")
    
    try:
        log.info(f"开始执行 Agent 分析: {symbol}, {market}, {discount_rate}, {growth_rate}, {total_shares}")
        result = await run_agent(symbol, market, discount_rate, growth_rate, total_shares, agent_names)
        log.info(f"Agent 执行结果: \n{result}")
    except Exception as e:
        log.error(f"""
        [ERROR] Agent 执行失败:
        - 类型: {type(e).__name__}
        - 消息: {str(e)}
        - 文件: {e.__traceback__.tb_frame.f_code.co_filename}
        - 行号: {e.__traceback__.tb_lineno}
        """, exc_info=True)

# if __name__ == "__main__":
#     asyncio.run(main(symbol="002963", market="cn", discount_rate=0.05, growth_rate=0.01, total_shares=100000000))
   