import json

def read_json(file_path)-> dict:
    """读取JSON文件"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data        
    except FileNotFoundError:
        print(f"文件路径错误：{file_path} 不存在")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON格式错误：第{e.lineno}行，错误原因：{e.msg}")
        return None
    
    
def read_file(file_path)-> str:
    """读取文件内容"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = f.read()
            return data        
    except FileNotFoundError:
        print(f"文件路径错误：{file_path} 不存在")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON格式错误：第{e.lineno}行，错误原因：{e.msg}")
        return None
    
def valid(content:str, name:str)->bool:
    if name == 'symbol':
        return content.isalpha()
    elif name == 'discount_rate':
        return 0 < float(content)< 1
    elif name == 'growth_rate':
        return -0.1 <float(content)<0.2