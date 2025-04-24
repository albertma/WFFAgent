from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_mcp.toolkit import MCPToolkit
from mcp import ClientSession, StdioServerParameters
#from tenacity import retry, stop_after_attempt
from mcp.client.stdio import stdio_client
import asyncio
from langchain_mcp.toolkit import MCPToolkit
from mcp.types import TextContent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import json
import os
import logging

logging.basicConfig(level=logging.DEBUG)  # 显示 MCP 协议层通信细节
# 异步初始化函数
ANALYST_PROMPT = """
你是一名资深证券分析师，需要完成以下任务：
分析的股票代码为:{symbol}的公司
1. 根据股票代码{symbol}和公司的当前股价计算最近5年的:
    - 营收增长率、毛利率, 费用率(销售费用,管理费用,研发费用,财务费用),EPS
    - 费用结构（营销费用，管理费用，研发费用，财务费用占收入的比值），以及费用结构的变化率，固定资产支出占总收入的比值
    - 固定资产占比，流动资产占比，流动负债占比，长期负债占比
    - 资产周转率，存货周转率，应收账款周转率，应付账款周转率，利息覆盖率=ebit/利息支出
    - 自由现金流，资本支出，自由现金流变化率，自由现金流占销售收入的比值
    - ROE（包括净利润率=Net Income/Revenue,总资产周转率=Revenue/Avg Assets, 权益乘数=Avg Assets / Avg Shareholder Equity)
    - 资产负债率，流动比率，速动比率
    - 根据当前股价和EPS计算的市盈率PE，市净率PB
    - 使用自由现金流折价模型的估值，对计算合理股价根据用户输入的过去三年的自由现金流增长率，计算未来5年的自由现金流，询问用户折现率和终值增长率
    等关键指标
2. 分析指标中的异常波动，结合行业数据进行对比分析，给出总结
3. 生成一份完整的财务分析报告，包含以上所有分析结果和结论
请注意，以上任务需要分步骤执行，每次调用工具后验证数据准确性。请根据实际情况调整分析的深度和广度。
    """
api_key = os.getenv("DEEPSEEK_API_KEY")  # 推荐使用环境变量存储

# 定义读取文件的函数
def readFile(file_path):
    """读取文件内容"""
    with os.open(file_path, 'r') as file:
        return file.read()

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
            # indicators = parse_mcp_response(result)
            # print(f"计算出的财务指标: {indicators}")
            


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

async def run_agent():
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
            "symbol": "AAPL",
            "user_requirement": "输出Markdown格式的财报分析报告",
            })

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
    
    
    
  
if __name__ == "__main__":
    #asyncio.run(test_server())
    asyncio.run(main())
   