from concurrent import futures
from typing import Any, Dict, List
from wff_agent.datasource import akshare_request as ak_request
import logging

log = logging.getLogger(__name__)           

def get_macro_data(markets: List[str]) -> Dict[str, Any]:
    """获取宏观数据
    Args:
        markets: 市场列表，支持 "us" 和 "cn"
    Returns:
        Dict[str, Any]: 宏观数据，包含指定市场的各项指标数据
    """
    if not markets:
        return {}

    # 定义所有可用的任务
    all_tasks = {
        "美国劳动力指数": ak_request.get_labor_index,
        "美国CPI": ak_request.get_us_cpi,
        "美国利率": ak_request.get_usa_interest_rate,
        "中国PPI": ak_request.get_cn_ppi,
        "中国CPI": ak_request.get_cn_cpi,
        "中国利率": ak_request.get_cn_cx_pmi,
    }
    
    # 根据市场参数筛选任务
    tasks = {}
    for task_name, task_func in all_tasks.items():
        if ("美国" in task_name and "us" in markets) or ("中国" in task_name and "cn" in markets):
            tasks[task_name] = task_func
    
    results = {}
    with futures.ThreadPoolExecutor(max_workers=len(tasks)) as executor:
        future_to_task = {
            executor.submit(task): name 
            for name, task in tasks.items()
        }
        
        for future in futures.as_completed(future_to_task):
            task_name = future_to_task[future]
            try:
                df = future.result()
                results[task_name] = df.to_dict(orient="records") if df is not None else None
            except Exception as e:
                log.error(f"获取{task_name}数据时发生错误: {str(e)}")
                results[task_name] = None
    
    return results

if __name__ == "__main__":
    # 测试获取美国和中国数据
    #print(get_macro_data(["us", "cn"]))
    # 测试只获取美国数据
    print(get_macro_data(["us"]))
    # 测试只获取中国数据
    #print(get_macro_data(["cn"]))
