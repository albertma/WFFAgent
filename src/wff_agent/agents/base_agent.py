import logging
from typing import Any, Dict, List
from abc import ABC, abstractmethod

# 第三方库导入
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_mcp.toolkit import MCPToolkit
from langchain_openai import ChatOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

log = logging.getLogger(__name__)

class AnalysisAgent(ABC):
    """基础 Agent 类，提供基本的 Agent 功能"""
    
    def __init__(self, 
                 base_url:str, 
                 api_key:str, 
                 model:str, 
                 temperature:float, 
                 max_tokens:int):
        """初始化基础 Agent"""
        self.llm = self._create_llm(base_url, api_key, 
                                    model, temperature, 
                                    max_tokens)
        
    def _create_llm(self, base_url:str, api_key:str, model:str, 
                    temperature:float, max_tokens:int) -> ChatOpenAI:
        """创建语言模型实例"""
        return ChatOpenAI(
            base_url=base_url,
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    @abstractmethod
    def get_registered_tools(self) -> List[str]:
        """获取注册的工具列表
        
        Returns:
            List[str]: 工具名称列表
        """
        pass
    
    def create_toolkit(self, session: ClientSession = None) -> MCPToolkit:
        """创建工具包"""
        return MCPToolkit(
            mcp_servers={"financial": "stdio"},
            session=session,
            registered_tools=self.get_registered_tools()
        )
    
    def create_agent_executor(self, toolkit: MCPToolkit, system_prompt: str, user_message_prompt: str) -> AgentExecutor:
        """创建 Agent 执行器"""
        try:
            log.info("Creating agent... ChatPromptTemplate()")
            template = ChatPromptTemplate([
                ("system", system_prompt),
                ("user", user_message_prompt),
                MessagesPlaceholder("agent_scratchpad")
            ])
            
            tools = toolkit.get_tools()
            log.info(f"可用工具: {tools}")
            log.info("Creating agent... create_tool_calling_agent()")
            agent = create_tool_calling_agent(
                llm=self.llm,
                tools=tools,
                prompt=template,
            )
            
            log.info("Creating Agent Executor...")
            return AgentExecutor.from_agent_and_tools(
                agent=agent,
                tools=tools,
                handle_parsing_errors=lambda e: f"解析错误: {e}\n请检查输入格式",
                max_iterations=5,
                early_stopping_method="generate",
                return_intermediate_steps=True
            )
        except Exception as e:
            log.error(f"创建 Agent Executor 失败: {str(e)}", exc_info=True)
            raise

    async def execute_with_session(self, 
                                   system_prompt: str, 
                                   user_message_prompt: str, 
                                   input: Dict[str, Any]={}) -> str:
        """使用会话执行 Agent
        
        Args:
            system_prompt (str): 系统提示
            user_message_prompt (str): 用户消息模版
            input (Dict[str, Any]): 输入参数
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "wff_agent.mcp_server"]
        )
        
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    log.info("Initializing session...")
                    await session.initialize()
                    log.info("Attaching session to toolkit...")
                    toolkit = self.create_toolkit(session)
                    log.info("Initializing toolkit...")
                    await toolkit.initialize()
                    log.info(f"System prompt:{system_prompt}")
                    agent_executor = self.create_agent_executor(toolkit=toolkit, 
                                                                system_prompt=system_prompt, 
                                                                user_message_prompt=user_message_prompt)
                    log.info(f"Created agent executor: {self.__class__.__name__}, invoke executor with input: {input}")
                    content = await agent_executor.ainvoke(input=input)
                    return content['output']
        except Exception as e:
            log.error(f"运行 agent 失败: {str(e)}", exc_info=True)
            raise e

    @abstractmethod
    def prepare_input(self, input:Dict[str, Any], context:Dict[str, Any]) -> Dict[str, Any]:
        """准备输入"""
        pass
    
    @abstractmethod
    def get_user_prompt(self, input:Dict[str, Any], context:Dict[str, Any]) -> str:
        """获取用户提示"""
        pass
    
    @abstractmethod
    def get_output_file_name(self, input:Dict[str, Any]) -> str:
        """获取输出文件名"""
        pass