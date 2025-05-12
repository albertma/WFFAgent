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

logger = logging.getLogger()  # 根logger
logging.basicConfig(level=logging.DEBUG)
logger.addHandler(handler)

if __name__ == "__main__":
    #asyncio.run(main(symbol="TSLA", market="us", total_shares=100000000))
    print("start")
    try:
        asyncio.run(wff_agent.agent_client.main(
            symbol="00700", 
            market="hk", 
            discount_rate=0.05, 
            growth_rate=0.01, 
            total_shares=9190000000))
    except Exception as e:
        print(e)
    print("end")