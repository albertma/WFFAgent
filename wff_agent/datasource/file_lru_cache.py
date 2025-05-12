import datetime
import time
import hashlib
import os
from pathlib import Path
import pickle
from typing import Any, Callable, Optional

def get_cache_dir() -> Path:
    """
    获取缓存目录
    
    Returns:
        缓存目录路径
    """
    # 在项目根目录下创建.cache目录
    cache_dir = Path(os.path.dirname(os.path.dirname(__file__))) / ".cache"
    cache_dir.mkdir(exist_ok=True)
    return cache_dir

def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    生成缓存键
    
    Args:
        prefix: 前缀
        *args: 位置参数
        **kwargs: 关键字参数
        
    Returns:
        缓存键
    """
    # 将参数转换为字符串
    args_str = str(args) + str(sorted(kwargs.items()))
    # 计算MD5哈希
    hash_obj = hashlib.md5(args_str.encode())
    return f"{prefix}_{hash_obj.hexdigest()}"

def cache_data(data: Any, cache_key: str, expire_seconds: int = 3600) -> None:
    """
    缓存数据到本地
    
    Args:
        data: 要缓存的数据
        cache_key: 缓存键
        expire_seconds: 过期时间（秒）
    """
    cache_dir = get_cache_dir()
    cache_file = cache_dir / f"{cache_key}.pkl"
    
    
    # 保存数据和过期时间
    cache_data = {
        "data": data,
        "expire_time": datetime.datetime.now() + datetime.timedelta(seconds=expire_seconds)
    }
    
    try:
        with open(cache_file, "wb") as f:
            pickle.dump(cache_data, f)
    except Exception as e:
        print(f"缓存数据时出错: {str(e)}")
        
def get_cached_data(cache_key: str) -> Optional[Any]:
    """
    获取缓存数据
    
    Args:
        cache_key: 缓存键
        
    Returns:
        缓存的数据，如果不存在或已过期则返回None
    """
    cache_dir = get_cache_dir()
    cache_file = cache_dir / f"{cache_key}.pkl"
    
    if not cache_file.exists():
        return None
    
    try:
        with open(cache_file, "rb") as f:
            cache_data = pickle.load(f)
        
        # 检查是否过期
        expired_time  =  cache_data["expire_time"].timestamp()
        now_time = datetime.datetime.now()
        if now_time.timestamp() > expired_time :
            # 删除过期缓存
            os.remove(cache_file)
            return None
        
        return cache_data["data"]
    except Exception as e:
        print(f"读取缓存数据时出错: {str(e)}")
        return None
def cached(prefix: str, expire_seconds: int = 3600):
    """
    缓存装饰器
    
    Args:
        prefix: 缓存键前缀
        expire_seconds: 过期时间（秒）
        max_length: 缓存长度
    Returns:
        装饰器函数
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = generate_cache_key(prefix, *args, **kwargs)
            
            # 尝试从缓存获取数据
            cached_result = get_cached_data(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 调用原函数
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                print(f"call func {func.__name__} 出错: {str(e)}")
                raise ValueError(f"缓存装饰器时出错: {str(e)}")
            
            # 缓存结果
            cache_data(result, cache_key, expire_seconds)
            
            return result
        return wrapper
    return decorator

def clear_cache(prefix: Optional[str] = None) -> int:
    """
    清除缓存
    
    Args:
        prefix: 缓存键前缀，如果为None则清除所有缓存
        
    Returns:
        清除的缓存文件数量
    """
    cache_dir = get_cache_dir()
    count = 0
    
    for cache_file in cache_dir.glob("*.pkl"):
        if prefix is None or cache_file.name.startswith(f"{prefix}_"):
            try:
                os.remove(cache_file)
                count += 1
            except Exception as e:
                print(f"删除缓存文件 {cache_file} 时出错: {str(e)}")
    
    return count 