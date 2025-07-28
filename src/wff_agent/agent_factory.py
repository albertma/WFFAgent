

import os
from wff_agent.stock_agents import NewsAnalysisAgent
from wff_agent.stock_agents import TechAnalysisAgent
from wff_agent.stock_agents import FundamentalAnalysisAgent
from wff_agent.stock_agents import GlobalMarketAnalysisAgent
from wff_agent.stock_agents import ComprehensiveAnalysisAgent
llm_api_key = os.getenv("DEEPSEEK_API_KEY")
llm_base_url = os.getenv("DEEPSEEK_BASE_URL")
llm_model = "deepseek-chat"
class AgentFactory:
    _singleton = None
    
    @classmethod
    def instance(self):
        if AgentFactory._singleton is None:
            AgentFactory._singleton = AgentFactory()
        return AgentFactory._singleton
    
    def create_agent(self, agent_name: str):
        if agent_name == "NewsAnalysisAgent":
            return NewsAnalysisAgent(
                base_url=llm_base_url,
                api_key=llm_api_key,
                model=llm_model,
                temperature= 0.3,
                max_tokens=64096)
        elif agent_name == "TechAnalysisAgent":
            return TechAnalysisAgent(
                base_url=llm_base_url,
                api_key=llm_api_key,
                model=llm_model,
                temperature= 0.1,
                max_tokens=64096)
        elif agent_name == "FundamentalAnalysisAgent":
            return FundamentalAnalysisAgent(
                base_url=llm_base_url,
                api_key=llm_api_key,
                model=llm_model,
                temperature= 0.1,
                max_tokens=64096)
        elif agent_name == "GlobalMarketAnalysisAgent":
            return GlobalMarketAnalysisAgent(
                base_url=llm_base_url,
                api_key=llm_api_key,
                model=llm_model,
                temperature= 0.1,
                max_tokens=64096)
        elif agent_name == "ComprehensiveAnalysisAgent":
            return ComprehensiveAnalysisAgent(
                base_url=llm_base_url,
                api_key=llm_api_key,
                model=llm_model,
                temperature= 0.1,
                max_tokens=64096)
        elif agent_name == "CryptoBTCTechAnalysisAgent":
            return CryptoBTCTechAnalysisAgent(
                base_url=llm_base_url,
                api_key=llm_api_key,
                model=llm_model,
                temperature= 0.1,
                max_tokens=64096)
        else:
            raise ValueError(f"Agent {agent_name} not found")