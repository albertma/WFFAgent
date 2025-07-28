#!/usr/bin/env python3
"""
股票分析Web UI界面
"""

import asyncio
import logging
import os
import sys
from typing import Dict, Any, Optional
import gradio as gr
from datetime import datetime
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wff_agent.agent_client import main as run_agent_analysis
from wff_agent.utils.stock_utils import is_valid_symbol

# 配置日志
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class StockAnalysisWebUI:
    """股票分析Web UI类"""
    
    def __init__(self):
        self.analysis_results = {}
        self.current_settings = {
            "symbol": "",
            "market": "cn",
            "discount_rate": 0.05,
            "growth_rate": 0.01,
            "total_shares": 0
        }
        self.progress_queue = asyncio.Queue()
        
    def create_ui(self):
        """创建Web UI界面"""
        
        # 自定义CSS样式
        css = """
        .gradio-container {
            max-width: 1200px !important;
            margin: 0 auto !important;
        }
        .header {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .settings-panel {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .analysis-panel {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .result-panel {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }
        .status-success {
            color: #28a745;
            font-weight: bold;
        }
        .status-error {
            color: #dc3545;
            font-weight: bold;
        }
        .status-warning {
            color: #ffc107;
            font-weight: bold;
        }
        """
        
        with gr.Blocks(css=css, title="股票分析智能助手") as demo:
            
            # 页面标题
            gr.HTML("""
            <div class="header">
                <h1>🤖 股票分析智能助手</h1>
                <p>专业的股票技术面、基本面、新闻情绪和全球市场分析</p>
                <div style="margin-top: 10px; font-size: 14px; opacity: 0.9;">
                    <span style="background: rgba(255,255,255,0.2); padding: 4px 8px; border-radius: 4px; margin-right: 10px;">
                        📦 版本 v0.05
                    </span>
                    <span style="background: rgba(255,255,255,0.2); padding: 4px 8px; border-radius: 4px;">
                        🔄 最新更新: 2025-01-07
                    </span>
                </div>
            </div>
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    # 设置面板
                    with gr.Group(elem_classes="settings-panel"):
                        gr.Markdown("### ⚙️ 分析参数设置")
                        
                        with gr.Row():
                            symbol_input = gr.Textbox(
                                label="股票代码",
                                placeholder="例如: 000001, AAPL, 00700",
                                value=""
                            )
                            market_dropdown = gr.Dropdown(
                                label="市场",
                                choices=["cn", "us", "hk"],
                                value="cn",
                                info="cn: 中国, us: 美国, hk: 香港"
                            )
                        
                        with gr.Row():
                            discount_rate_input = gr.Slider(
                                label="折现率",
                                minimum=0.01,
                                maximum=0.20,
                                value=0.05,
                                step=0.01,
                                info="用于DCF估值模型"
                            )
                            growth_rate_input = gr.Slider(
                                label="增长率",
                                minimum=0.00,
                                maximum=0.10,
                                value=0.01,
                                step=0.01,
                                info="永续增长率"
                            )
                        
                        total_shares_input = gr.Number(
                            label="总股本(可选)",
                            value=0,
                            info="港股需要填写总股本"
                        )
                        
                        validate_btn = gr.Button("✅ 验证股票代码", variant="primary")
                        status_text = gr.Textbox(label="验证状态", interactive=False)
                        
                        # 版本信息和改动叙述
                        with gr.Accordion("📋 版本信息与更新日志", open=False):
                            gr.Markdown("""
                            ### 🆕 v0.05 更新内容
                            
                            **✨ 新功能:**
                            - 新增全球市场分析功能
                            - 优化股票代码验证机制
                            - 改进UI界面设计，提升用户体验
                            
                            **🔧 改进:**
                            - 增强数据分析准确性
                            - 优化内存使用效率
                            - 修复已知bug和稳定性问题
                            
                            **📊 技术改进:**
                            - 升级依赖包版本
                            - 优化API调用频率
                            - 改进错误处理机制
                            
                            **🎯 性能提升:**
                            - 分析速度提升约30%
                            - 减少API调用次数
                            - 优化数据缓存机制
                            
                            ---
                            *最后更新: 2025-07-28*
                            """)
                
                with gr.Column(scale=2):
                    # 分析控制面板
                    with gr.Group(elem_classes="analysis-panel"):
                        gr.Markdown("### 📊 分析控制")
                        
                        with gr.Row():
                            complete_analysis_btn = gr.Button(
                                "🚀 运行完整分析", 
                                variant="primary",
                                size="lg"
                            )
                            single_analysis_btn = gr.Button(
                                "📈 单项分析", 
                                variant="secondary",
                                size="lg"
                            )
                        
                        analysis_type_dropdown = gr.Dropdown(
                            label="分析类型",
                            choices=[
                                "ComprehensiveAnalysisAgent",
                                "TechAnalysisAgent", 
                                "FundamentalAnalysisAgent",
                                "NewsAnalysisAgent",
                                "GlobalMarketAnalysisAgent"
                            ],
                            value="ComprehensiveAnalysisAgent",
                            visible=False
                        )
                        
                        progress_text = gr.Textbox(
                            label="分析进度", 
                            interactive=False,
                            lines=3
                        )
            
            # 结果显示面板
            with gr.Group(elem_classes="result-panel"):
                gr.Markdown("### 📋 分析结果")
                
                with gr.Tabs():
                    with gr.TabItem("📊 综合分析"):
                        comprehensive_result = gr.Markdown(
                            value="等待分析结果...",
                            label="综合分析报告"
                        )
                    
                    with gr.TabItem("📈 技术分析"):
                        technical_result = gr.Markdown(
                            value="等待分析结果...",
                            label="技术分析报告"
                        )
                    
                    with gr.TabItem("💰 基本面分析"):
                        fundamental_result = gr.Markdown(
                            value="等待分析结果...",
                            label="基本面分析报告"
                        )
                    
                    with gr.TabItem("📰 新闻分析"):
                        news_result = gr.Markdown(
                            value="等待分析结果...",
                            label="新闻分析报告"
                        )
                    
                    with gr.TabItem("🌍 全球市场"):
                        global_result = gr.Markdown(
                            value="等待分析结果...",
                            label="全球市场分析报告"
                        )
                    
                    with gr.TabItem("⚙️ 当前设置"):
                        settings_display = gr.JSON(
                            value={},
                            label="当前分析参数"
                        )
            
            # 事件处理函数
            def validate_symbol(symbol, market):
                """验证股票代码"""
                if not symbol:
                    return "❌ 请输入股票代码"
                
                if is_valid_symbol(symbol, market):
                    self.current_settings["symbol"] = symbol
                    self.current_settings["market"] = market
                    return f"✅ 股票代码 {symbol} ({market}) 验证通过"
                else:
                    return f"❌ 股票代码 {symbol} ({market}) 无效"
            
            def update_settings(symbol, market, discount_rate, growth_rate, total_shares):
                """更新设置"""
                self.current_settings.update({
                    "symbol": symbol,
                    "market": market,
                    "discount_rate": discount_rate,
                    "growth_rate": growth_rate,
                    "total_shares": total_shares
                })
                return self.current_settings
            
            def progress_callback(step_name: str, result: str, status: str = "completed"):
                """进度回调函数"""
                try:
                    # 将进度信息放入队列
                    asyncio.create_task(self.progress_queue.put({
                        "step_name": step_name,
                        "result": result,
                        "status": status
                    }))
                except Exception as e:
                    log.error(f"进度回调执行失败: {e}")
            
            async def run_complete_analysis(symbol, market, discount_rate, growth_rate, total_shares):
                """运行完整分析"""
                if not symbol or not market:
                    return "❌ 请先设置股票代码和市场"
                
                if not is_valid_symbol(symbol, market):
                    return "❌ 股票代码无效，请先验证"
                
                try:
                    progress_text = "⏳ 开始分析...\n"
                    progress_text += f"股票代码: {symbol}\n"
                    progress_text += f"市场: {market}\n"
                    progress_text += f"参数: 折现率={discount_rate}, 增长率={growth_rate}\n"
                    
                    # 清空之前的结果
                    self.analysis_results = {}
                    
                    # 运行分析
                    result = await run_agent_analysis(
                        symbol=symbol,
                        market=market,
                        discount_rate=discount_rate,
                        growth_rate=growth_rate,
                        total_shares=total_shares,
                        progress_callback=progress_callback
                    )
                    
                    self.analysis_results = result
                    progress_text += "✅ 分析完成！"
                    
                    return progress_text
                    
                except Exception as e:
                    error_msg = f"❌ 分析失败: {str(e)}"
                    log.error(f"完整分析失败: {e}", exc_info=True)
                    return error_msg
            
            async def run_single_analysis(symbol, market, discount_rate, growth_rate, total_shares, analysis_type):
                """运行单项分析"""
                if not symbol or not market:
                    return "❌ 请先设置股票代码和市场"
                
                if not is_valid_symbol(symbol, market):
                    return "❌ 股票代码无效，请先验证"
                
                try:
                    progress_text = f"⏳ 开始{analysis_type}分析...\n"
                    progress_text += f"股票代码: {symbol}\n"
                    progress_text += f"市场: {market}\n"
                    
                    # 清空之前的结果
                    self.analysis_results = {}
                    
                    # 运行单项分析
                    result = await run_agent_analysis(
                        symbol=symbol,
                        market=market,
                        discount_rate=discount_rate,
                        growth_rate=growth_rate,
                        total_shares=total_shares,
                        agent_names=[analysis_type],
                        progress_callback=progress_callback
                    )
                    
                    self.analysis_results = result
                    progress_text += "✅ 分析完成！"
                    
                    return progress_text
                    
                except Exception as e:
                    error_msg = f"❌ 分析失败: {str(e)}"
                    log.error(f"单项分析失败: {e}", exc_info=True)
                    return error_msg
            
            def update_results():
                """更新结果显示"""
                if not self.analysis_results:
                    return {
                        comprehensive_result: "暂无分析结果",
                        technical_result: "暂无分析结果", 
                        fundamental_result: "暂无分析结果",
                        news_result: "暂无分析结果",
                        global_result: "暂无分析结果"
                    }
                
                results = {}
                
                # 更新各个分析结果
                for agent_name, result in self.analysis_results.items():
                    if isinstance(result, dict) and 'output' in result:
                        if 'Comprehensive' in agent_name:
                            results[comprehensive_result] = result['output']
                        elif 'Tech' in agent_name:
                            results[technical_result] = result['output']
                        elif 'Fundamental' in agent_name:
                            results[fundamental_result] = result['output']
                        elif 'News' in agent_name:
                            results[news_result] = result['output']
                        elif 'Global' in agent_name:
                            results[global_result] = result['output']
                
                return results
            
            async def update_single_result(step_name: str, result: str):
                """更新单个分析结果"""
                # 根据步骤名称更新对应的结果显示
                if 'Tech' in step_name:
                    return {technical_result: result}
                elif 'Fundamental' in step_name:
                    return {fundamental_result: result}
                elif 'News' in step_name:
                    return {news_result: result}
                elif 'Global' in step_name:
                    return {global_result: result}
                elif 'Comprehensive' in step_name:
                    return {comprehensive_result: result}
                else:
                    return {}
            
            # 绑定事件
            validate_btn.click(
                fn=validate_symbol,
                inputs=[symbol_input, market_dropdown],
                outputs=[status_text]
            )
            
            # 更新设置
            for input_component in [symbol_input, market_dropdown, discount_rate_input, growth_rate_input, total_shares_input]:
                input_component.change(
                    fn=update_settings,
                    inputs=[symbol_input, market_dropdown, discount_rate_input, growth_rate_input, total_shares_input],
                    outputs=[settings_display]
                )
            
            # 完整分析
            complete_analysis_btn.click(
                fn=run_complete_analysis,
                inputs=[symbol_input, market_dropdown, discount_rate_input, growth_rate_input, total_shares_input],
                outputs=[progress_text]
            ).then(
                fn=update_results,
                outputs=[comprehensive_result, technical_result, fundamental_result, news_result, global_result]
            )
            
            # 单项分析
            single_analysis_btn.click(
                fn=lambda: gr.Dropdown(visible=True),
                outputs=[analysis_type_dropdown]
            )
            
            analysis_type_dropdown.change(
                fn=run_single_analysis,
                inputs=[symbol_input, market_dropdown, discount_rate_input, growth_rate_input, total_shares_input, analysis_type_dropdown],
                outputs=[progress_text]
            ).then(
                fn=update_results,
                outputs=[comprehensive_result, technical_result, fundamental_result, news_result, global_result]
            )
            
            # 初始化设置显示
            demo.load(
                fn=lambda: self.current_settings,
                outputs=[settings_display]
            )
        
        return demo

def create_web_ui():
    """创建Web UI实例"""
    ui = StockAnalysisWebUI()
    return ui.create_ui()

if __name__ == "__main__":
    # 创建并启动Web UI
    demo = create_web_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    ) 