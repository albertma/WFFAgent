#!/usr/bin/env python3
"""
简化版股票分析Web UI
"""

import os
import sys
import logging
from typing import Dict, Any
import gradio as gr
from datetime import datetime
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class SimpleStockAnalysisUI:
    """简化版股票分析UI"""
    
    def __init__(self):
        self.analysis_history = []
        
    def create_ui(self):
        """创建简化版UI"""
        
        # 自定义CSS
        css = """
        .gradio-container {
            max-width: 1000px !important;
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
        .input-panel {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .result-panel {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        """
        
        with gr.Blocks(css=css, title="股票分析助手") as demo:
            
            # 页面标题
            gr.HTML("""
            <div class="header">
                <h1>📈 股票分析助手</h1>
                <p>简化版股票分析工具 - 快速获取股票信息</p>
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
                    # 输入面板
                    with gr.Group(elem_classes="input-panel"):
                        gr.Markdown("### 📝 输入参数")
                        
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
                            discount_rate = gr.Slider(
                                label="折现率",
                                minimum=0.01,
                                maximum=0.20,
                                value=0.05,
                                step=0.01
                            )
                            growth_rate = gr.Slider(
                                label="增长率",
                                minimum=0.00,
                                maximum=0.10,
                                value=0.01,
                                step=0.01
                            )
                        
                        analyze_btn = gr.Button("🚀 开始分析", variant="primary", size="lg")
                        
                        # 版本信息面板
                        with gr.Accordion("📋 版本信息", open=False):
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
                    # 结果显示面板
                    with gr.Group(elem_classes="result-panel"):
                        gr.Markdown("### 📊 分析结果")
                        
                        with gr.Tabs():
                            with gr.TabItem("📈 基本信息"):
                                basic_info = gr.Markdown(
                                    value="等待分析...",
                                    label="股票基本信息"
                                )
                            
                            with gr.TabItem("💰 财务分析"):
                                financial_analysis = gr.Markdown(
                                    value="等待分析...",
                                    label="财务分析报告"
                                )
                            
                            with gr.TabItem("📰 市场情绪"):
                                market_sentiment = gr.Markdown(
                                    value="等待分析...",
                                    label="市场情绪分析"
                                )
                            
                            with gr.TabItem("📋 分析历史"):
                                history_display = gr.JSON(
                                    value=[],
                                    label="分析历史记录"
                                )
            
            # 事件处理函数
            def validate_inputs(symbol, market):
                """验证输入"""
                if not symbol:
                    return "❌ 请输入股票代码", "❌ 请输入股票代码", "❌ 请输入股票代码", []
                
                # 简单的股票代码验证
                if market == "cn" and not (symbol.isdigit() and len(symbol) == 6):
                    return f"❌ 中国股票代码格式错误: {symbol}", "❌ 股票代码无效", "❌ 股票代码无效", []
                elif market == "us" and not symbol.isalpha():
                    return f"❌ 美国股票代码格式错误: {symbol}", "❌ 股票代码无效", "❌ 股票代码无效", []
                elif market == "hk" and not (symbol.isdigit() and len(symbol) == 5):
                    return f"❌ 香港股票代码格式错误: {symbol}", "❌ 股票代码无效", "❌ 股票代码无效", []
                
                return f"✅ 股票代码 {symbol} 验证通过", "✅ 股票代码有效", "✅ 股票代码有效", []
            
            def generate_basic_analysis(symbol, market, discount_rate, growth_rate):
                """生成基础分析"""
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                basic_info = f"""
# 📈 {symbol} 股票基本信息

## 基本信息
- **股票代码**: {symbol}
- **市场**: {market.upper()}
- **分析时间**: {current_time}

## 估值参数
- **折现率**: {discount_rate:.1%}
- **增长率**: {growth_rate:.1%}

## 模拟数据
- **当前价格**: ¥{100 + hash(symbol) % 50:.2f}
- **52周最高**: ¥{120 + hash(symbol) % 30:.2f}
- **52周最低**: ¥{80 + hash(symbol) % 20:.2f}
- **市值**: {1000 + hash(symbol) % 500}亿元

## 技术指标
- **RSI**: {30 + hash(symbol) % 40:.1f}
- **MACD**: {'买入' if hash(symbol) % 2 == 0 else '卖出'}
- **布林带**: {'上轨' if hash(symbol) % 3 == 0 else '中轨' if hash(symbol) % 3 == 1 else '下轨'}

---
*注: 这是模拟数据，仅供参考*
                """
                
                return basic_info
            
            def generate_financial_analysis(symbol, market, discount_rate, growth_rate):
                """生成财务分析"""
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 模拟财务数据
                revenue = 1000 + hash(symbol) % 500
                profit = revenue * (0.1 + hash(symbol) % 20 / 100)
                pe_ratio = 10 + hash(symbol) % 20
                pb_ratio = 1 + hash(symbol) % 5
                
                financial_analysis = f"""
# 💰 {symbol} 财务分析报告

## 财务指标
- **营业收入**: {revenue}亿元
- **净利润**: {profit:.1f}亿元
- **净利润率**: {profit/revenue*100:.1f}%
- **市盈率(PE)**: {pe_ratio:.1f}
- **市净率(PB)**: {pb_ratio:.1f}

## DCF估值
- **折现率**: {discount_rate:.1%}
- **增长率**: {growth_rate:.1%}
- **估值**: ¥{revenue * (1 + growth_rate) / (discount_rate - growth_rate):.2f}

## 财务健康度
- **流动比率**: {1.5 + hash(symbol) % 10 / 10:.1f}
- **资产负债率**: {40 + hash(symbol) % 30:.1f}%
- **ROE**: {8 + hash(symbol) % 12:.1f}%

## 投资建议
{'买入' if hash(symbol) % 2 == 0 else '持有' if hash(symbol) % 3 == 1 else '卖出'}

---
*分析时间: {current_time}*
*注: 这是模拟数据，仅供参考*
                """
                
                return financial_analysis
            
            def generate_market_sentiment(symbol, market):
                """生成市场情绪分析"""
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 模拟情绪数据
                sentiment_score = 50 + hash(symbol) % 50
                news_count = 10 + hash(symbol) % 20
                positive_ratio = 60 + hash(symbol) % 30
                
                sentiment_analysis = f"""
# 📰 {symbol} 市场情绪分析

## 情绪指标
- **情绪得分**: {sentiment_score}/100
- **新闻数量**: {news_count}条
- **正面新闻比例**: {positive_ratio}%

## 情绪状态
{'😊 积极' if sentiment_score > 70 else '😐 中性' if sentiment_score > 40 else '😞 消极'}

## 热门新闻
1. {symbol}发布最新财报，业绩超预期
2. 分析师上调{symbol}目标价
3. {symbol}获得重要合同
4. 行业政策利好{symbol}发展

## 技术面情绪
- **成交量**: {'放量' if hash(symbol) % 2 == 0 else '缩量'}
- **资金流向**: {'净流入' if hash(symbol) % 2 == 0 else '净流出'}
- **机构评级**: {'买入' if hash(symbol) % 2 == 0 else '持有'}

## 市场预期
- **短期**: {'看涨' if hash(symbol) % 2 == 0 else '看跌'}
- **中期**: {'震荡' if hash(symbol) % 3 == 0 else '上涨' if hash(symbol) % 3 == 1 else '下跌'}
- **长期**: {'看好' if hash(symbol) % 2 == 0 else '谨慎'}

---
*分析时间: {current_time}*
*注: 这是模拟数据，仅供参考*
                """
                
                return sentiment_analysis
            
            def run_analysis(symbol, market, discount_rate, growth_rate):
                """运行分析"""
                try:
                    # 验证输入
                    basic_status, financial_status, sentiment_status, history = validate_inputs(symbol, market)
                    
                    if "❌" in basic_status:
                        return basic_status, financial_status, sentiment_status, history
                    
                    # 生成分析结果
                    basic_result = generate_basic_analysis(symbol, market, discount_rate, growth_rate)
                    financial_result = generate_financial_analysis(symbol, market, discount_rate, growth_rate)
                    sentiment_result = generate_market_sentiment(symbol, market)
                    
                    # 更新历史记录
                    analysis_record = {
                        "timestamp": datetime.now().isoformat(),
                        "symbol": symbol,
                        "market": market,
                        "discount_rate": discount_rate,
                        "growth_rate": growth_rate,
                        "status": "completed"
                    }
                    
                    self.analysis_history.append(analysis_record)
                    if len(self.analysis_history) > 10:  # 只保留最近10条记录
                        self.analysis_history = self.analysis_history[-10:]
                    
                    return basic_result, financial_result, sentiment_result, self.analysis_history
                    
                except Exception as e:
                    error_msg = f"❌ 分析失败: {str(e)}"
                    log.error(f"分析失败: {e}", exc_info=True)
                    return error_msg, error_msg, error_msg, self.analysis_history
            
            # 绑定事件
            analyze_btn.click(
                fn=run_analysis,
                inputs=[symbol_input, market_dropdown, discount_rate, growth_rate],
                outputs=[basic_info, financial_analysis, market_sentiment, history_display]
            )
            
            # 初始化历史记录
            demo.load(
                fn=lambda: self.analysis_history,
                outputs=[history_display]
            )
        
        return demo

def create_simple_web_ui():
    """创建简化版Web UI"""
    ui = SimpleStockAnalysisUI()
    return ui.create_ui()

if __name__ == "__main__":
    # 创建并启动简化版Web UI
    demo = create_simple_web_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=False,
        show_error=True
    ) 