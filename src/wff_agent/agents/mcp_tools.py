# -*- coding: utf-8 -*-
from autogen_ext.tools.mcp import (
    StdioServerParams,
    SseServerParams,
    mcp_server_tools
)
import os

async def get_stdio_tools(mcp_file_path:str) -> list:
    print(f"########################Get stdio tools: {mcp_file_path}")
    
    server_params = StdioServerParams(
        command="python",
        args=["-m", f"{mcp_file_path}"],
        env={
            "NEWS_API_KEY": os.getenv("NEWS_API_KEY"),
            "ALPHA_VANTAGE_API_KEY": os.getenv("ALPHA_VANTAGE_API_KEY")
        }
    )   
    return await mcp_server_tools(server_params)

async def get_sse_tools(url_address_port:str, access_key:str = "") -> list:
   
    server_params = SseServerParams(
        url=f"{url_address_port}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_key}"
        }
    )
    return await mcp_server_tools(server_params)

