# -*- coding: utf-8 -*-
from autogen_ext.tools.mcp import (
    StdioServerParams,
    SseServerParams,
    mcp_server_tools
)

async def get_stdio_tools(mcp_file_path:str) -> list:
    print(f"mcp_file_path: {mcp_file_path}")
    server_params = StdioServerParams(
        command="python",
        args=["-m", f"{mcp_file_path}"]  # 确保指向正确的服务器文件路径
    )   
    return await mcp_server_tools(server_params)

async def get_sse_tools(url_address_port:str, access_key:str = None) -> list:
   
    server_params = SseServerParams(
        url=f"{url_address_port}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_key}"
        }
    )
    return await mcp_server_tools(server_params)

