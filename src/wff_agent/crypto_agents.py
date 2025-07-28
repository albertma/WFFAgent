from wff_agent.agents import AnalysisAgent
from wff_agent.prompts import CryptoNewsAnalysisPrompt

class CryptoBTCTechAnalysisAgent(AnalysisAgent):
    def __init__(self):
        super().__init__()
        self.name = "CryptoNewsAnalysisAgent"
        self.description = "CryptoNewsAnalysisAgent 是一个分析加密货币新闻的 agent"
        self.prompt = CryptoNewsAnalysisPrompt

    def run(self, news: str):
        return self.prompt.format(news=news)