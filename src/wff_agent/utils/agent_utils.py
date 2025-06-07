import json
import logging
from mcp.types import TextContent
log = logging.getLogger(__name__)

def read_json(file_path)-> dict:
    """读取JSON文件"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data        
    except FileNotFoundError:
        log.error(f"文件路径错误：{file_path} 不存在")
        return None
    except json.JSONDecodeError as e:
        log.error(f"JSON格式错误：第{e.lineno}行，错误原因：{e.msg}")
        return None
    
    
def read_file(file_path)-> str:
    """读取文件内容"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = f.read()
            return data        
    except FileNotFoundError:
        log.error(f"文件路径错误：{file_path} 不存在")
        return None
    except json.JSONDecodeError as e:
        log.error(f"JSON格式错误：第{e.lineno}行，错误原因：{e.msg}")
        return None
    

def parse_mcp_response(response) -> dict:
    """解析 MCP 响应"""
    if not response.isError:
        for content_item in response.content:
            if isinstance(content_item, TextContent) and content_item.type == 'text':
                try:
                    return json.loads(content_item.text)
                except json.JSONDecodeError:
                    log.error("Invalid JSON format in TextContent")
                    raise ValueError("Invalid JSON format in TextContent")
    else:
        log.error(f"Error: {response.error}")
        raise ValueError(f"MCP Response Error: {response.error}")