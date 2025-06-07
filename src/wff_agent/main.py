import asyncio

import wff_agent.agent_client
#from wff_agent.agent_main import main
import logging
from logging.handlers import TimedRotatingFileHandler

log_file = 'wff_agent.log'
handler = TimedRotatingFileHandler(
    log_file, when='midnight', interval=1, backupCount=7, encoding='utf-8'
)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
log.addHandler(handler)

if __name__ == "__main__":
    #asyncio.run(main(symbol="TSLA", market="us", total_shares=100000000))
    log.info("开始执行 Agent 工作流")
    try:
        asyncio.run(
            wff_agent.agent_client.main(
                symbol="LULU", 
                market="us", 
                discount_rate=0.05, 
                growth_rate=0.02, 
                total_shares=1.9*(10**9)
            )
        )
    except Exception as e:
        log.error(e)
    log.info("end")