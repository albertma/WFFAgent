from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_mcp.toolkit import MCPToolkit
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
from typing import Dict, Any
from uuid import uuid4
from langchain_mcp.toolkit import MCPToolkit
from mcp.types import TextContent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import json
import os
import logging
import agent_utils


logging.basicConfig(level=logging.DEBUG)  # 显示 MCP 协议层通信细节
# 异步初始化函数

api_key = os.getenv("DEEPSEEK_API_KEY")  # 推荐使用环境变量存储

#reading prompt   
ANALYST_PROMPT = agent_utils.read_file("PROMPT.txt")

class SessionState:
    def __init__(self):
        self.sessions: Dict[str, dict] = {} 
    
    def has_session(self, session_id:str):
        return self.sessions.keys().__contains__(session_id)
    
    def create_session(self, session_id:str) -> str:
        self.sessions[session_id] = {
            "stage": "init",  # 对话阶段标识
            "params": {}
        }
        return session_id

    def update_param(self, session_id: str, key: str, value: Any):
        self.sessions[session_id]["params"][key] = value

    def set_stage(self, session_id: str, stage: str):
        old_stage = self.sessions[session_id]["stage"]
        print(f"Session {session_id[:8]} 状态变更: {old_stage} → {stage}") 
        self.sessions[session_id]["stage"] = stage

session_state = SessionState()

def validate_parameters(params: dict):
    if not params["symbol"].isalpha():
        raise ValueError("股票代码必须为纯字母")
    if not (0 < params["discount_rate"] < 1):
        raise ValueError("折现率需在0-1之间")
    if not (-0.1 < params["growth_rate"] < 0.2):
        raise ValueError("增长率需在-10%到20%之间")

def parse_mcp_response(response)-> dict:
    if not response.isError:
        for content_item in response.content:
            if isinstance(content_item, TextContent) and content_item.type == 'text':
                try:
                    data = json.loads(content_item.text)
                    return data
                except json.JSONDecodeError:
                    raise ValueError("Invalid JSON format in TextContent")
    else:
        print(f"Error: {response.error}")
        
        
async def test_server():
    print("Testing server...")
    server_params = StdioServerParameters(
        command="python",
        args=["./mcp_server.py"]  # 确保指向正确的服务器文件路径
    )
     # 建立 MCP 连接
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化会话
            await session.initialize()
            tt = [t for t in await session.list_tools()]
            print("可用工具:", tt)

            # 调用服务器端工具
            #print(f"获取到的财报数据: {reports}")
            print("analyze_financials")
            result = await session.call_tool(
                "analyze_financials",
                { "symbol":"AAPL", "stock_price": 199.00}
            )
            print(f"计算结果: {result}")



def create_toolkit(session: ClientSession = None) -> MCPToolkit:
    # 创建工具包时不初始化会话
    toolkit = MCPToolkit(
        mcp_servers={"financial": "stdio"},
        session=session,  # 不传入会话对象
        registered_tools=[ 
                        "get_financial_statements",
                        "get_current_stockprice",
                        "analyze_financials",
                        "get_management_discussion"
                    ]
    )
    return toolkit



def create_agent_executor(toolkit: MCPToolkit) -> AgentExecutor:
    
    # 创建 OpenAI 模型实例
    print("Creating agent... ChatOpenAI()")
    llm = ChatOpenAI(
        base_url="https://api.deepseek.com/v1",
        api_key= api_key,  # 推荐环境变量存储
        model= "deepseek-chat",
        temperature = 0.3,
        max_tokens= 4000
    )
     # 创建 Agent（关键修复点）
    print("Creating agent... ChatPromptTemplate()")
    template = ChatPromptTemplate([
            ("system", ANALYST_PROMPT),
            ("user", "补充要求：{user_requirement}"),
            MessagesPlaceholder("agent_scratchpad")
            
        ])
    
    tools = toolkit.get_tools()
    print("tools:",tools)
    print("Creating agent... create_tool_calling_agent()")
    agent = create_tool_calling_agent(
        llm=llm,
        tools= tools,
        prompt= template,  # 使用自定义提示词
    )
    print("Creating Agent Executor...")
    # 创建 AgentExecutor
    return AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        handle_parsing_errors=lambda e: f"解析错误: {e}\n请检查输入格式",
        max_iterations=5,  # 防止无限重试
        early_stopping_method="generate",  # 错误时强制终止
        return_intermediate_steps=True  # 保留异常轨迹
        )

async def run_agent(symbol:str, discount_rate:float, growth_rate:float):
    print("Running agent...")
    server_params = StdioServerParameters(
        command="python",
        args=["./mcp_server.py"]  # 确保指向正确的服务器文件路径
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化会话
            print("Initializing session...")
            await session.initialize()
            toolkit = create_toolkit(session)
            await toolkit.initialize()
            # 将会话注入工具包
            print("Attaching session to toolkit...")
            print("Session attached to toolkit.")
            agent_executor = create_agent_executor(toolkit)
            print("Created agent Executor, invoke executor")
            return await agent_executor.ainvoke({
             "symbol": symbol,
             "discount_rate": discount_rate,
             "growth_rate":growth_rate,
             "user_requirement": "输出Markdown格式的财报分析报告",
            })


async def main():
    try:
        result = await run_agent()
        # 打印结果
        print("result:",result['output'])
    except Exception as e:
        error_msg = f"""
        [ERROR] Agent execution failed:
        - Type: {type(e).__name__}
        - Message: {str(e)}
        - Traceback: {e.__traceback__}
        - File: {e.__traceback__.tb_frame.f_code.co_filename}
        - Line: {e.__traceback__.tb_lineno}
        - Context: {e.__context__}
        """
        print(error_msg)  # 输出结构化错误信息[1,7](@ref)
  
if __name__ == "__main__":
    #asyncio.run(test_server())
    asyncio.run(main())
   