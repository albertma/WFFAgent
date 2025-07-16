import asyncio
import logging
from typing import Dict, Any, Optional
import os
from datetime import datetime

from wff_agent.agent_client import main as run_agent_analysis
from wff_agent.utils.stock_utils import is_valid_symbol

# 配置日志
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class InteractiveDialogue:
    """交互式股票分析对话系统"""
    
    def __init__(self):
        self.current_symbol = None
        self.current_market = None
        self.discount_rate = 0.05
        self.growth_rate = 0.01
        self.total_shares = 0
        self.analysis_results = {}
        
    def print_welcome(self):
        """打印欢迎信息"""
        print("=" * 60)
        print("🤖 欢迎使用股票分析智能助手")
        print("=" * 60)
        print("本系统提供以下功能：")
        print("1. 股票代码验证")
        print("2. 技术面分析")
        print("3. 基本面分析") 
        print("4. 新闻情绪分析")
        print("5. 全球市场分析")
        print("6. 综合分析报告")
        print("7. 参数设置")
        print("8. 退出系统")
        print("=" * 60)
        
    def print_menu(self):
        """打印主菜单"""
        print("\n📋 主菜单:")
        print("1. 设置股票代码")
        print("2. 设置分析参数")
        print("3. 运行完整分析")
        print("4. 运行单项分析")
        print("5. 查看分析结果")
        print("6. 查看当前设置")
        print("7. 帮助")
        print("8. 退出")
        
    def get_user_input(self, prompt: str, default: str = "") -> str:
        """获取用户输入"""
        if default:
            user_input = input(f"{prompt} (默认: {default}): ").strip()
            return user_input if user_input else default
        else:
            return input(f"{prompt}: ").strip()
            
    def set_stock_symbol(self):
        """设置股票代码"""
        print("\n📈 设置股票代码")
        print("支持的市场: cn(中国), us(美国), hk(香港)")
        
        symbol = self.get_user_input("请输入股票代码")
        if not symbol:
            print("❌ 股票代码不能为空")
            return
            
        market = self.get_user_input("请输入市场代码", "cn")
        
        # 验证股票代码
        if is_valid_symbol(symbol, market):
            self.current_symbol = symbol
            self.current_market = market
            print(f"✅ 股票代码设置成功: {symbol} ({market})")
        else:
            print(f"❌ 股票代码无效: {symbol} ({market})")
            
    def set_analysis_parameters(self):
        """设置分析参数"""
        print("\n⚙️ 设置分析参数")
        
        try:
            discount_rate = float(self.get_user_input("请输入折现率", str(self.discount_rate)))
            self.discount_rate = discount_rate
            
            growth_rate = float(self.get_user_input("请输入增长率", str(self.growth_rate)))
            self.growth_rate = growth_rate
            
            total_shares = int(self.get_user_input("请输入总股本(可选)", str(self.total_shares)))
            self.total_shares = total_shares
            
            print("✅ 参数设置成功")
        except ValueError as e:
            print(f"❌ 参数格式错误: {e}")
            
    async def run_complete_analysis(self):
        """运行完整分析"""
        if not self.current_symbol or not self.current_market:
            print("❌ 请先设置股票代码")
            return
            
        print(f"\n🔍 开始分析股票: {self.current_symbol} ({self.current_market})")
        print("⏳ 正在运行分析，请稍候...")
        
        try:
            result = await run_agent_analysis(
                symbol=self.current_symbol,
                market=self.current_market,
                discount_rate=self.discount_rate,
                growth_rate=self.growth_rate,
                total_shares=self.total_shares
            )
            
            self.analysis_results = result
            print("✅ 分析完成")
            
        except Exception as e:
            print(f"❌ 分析失败: {e}")
            
    async def run_single_analysis(self):
        """运行单项分析"""
        if not self.current_symbol or not self.current_market:
            print("❌ 请先设置股票代码")
            return
            
        print("\n📊 单项分析选项:")
        print("1. 技术面分析")
        print("2. 基本面分析")
        print("3. 新闻情绪分析")
        print("4. 全球市场分析")
        print("5. 综合分析")
        
        choice = self.get_user_input("请选择分析类型", "5")
        
        agent_mapping = {
            "1": ["TechAnalysisAgent"],
            "2": ["FundamentalAnalysisAgent"],
            "3": ["NewsAnalysisAgent"],
            "4": ["GlobalMarketAnalysisAgent"],
            "5": ["ComprehensiveAnalysisAgent"]
        }
        
        if choice in agent_mapping:
            agent_names = agent_mapping[choice]
            analysis_names = {
                "1": "技术面分析",
                "2": "基本面分析", 
                "3": "新闻情绪分析",
                "4": "全球市场分析",
                "5": "综合分析"
            }
            
            print(f"\n🔍 开始{analysis_names[choice]}...")
            
            try:
                result = await run_agent_analysis(
                    symbol=self.current_symbol,
                    market=self.current_market,
                    discount_rate=self.discount_rate,
                    growth_rate=self.growth_rate,
                    total_shares=self.total_shares,
                    agent_names=agent_names
                )
                
                self.analysis_results = result
                print("✅ 分析完成")
                
            except Exception as e:
                print(f"❌ 分析失败: {e}")
        else:
            print("❌ 无效选择")
            
    def show_analysis_results(self):
        """显示分析结果"""
        if not self.analysis_results:
            print("❌ 暂无分析结果")
            return
            
        print("\n📊 分析结果:")
        print("=" * 60)
        
        for step_name, step_result in self.analysis_results.items():
            if isinstance(step_result, dict) and 'output' in step_result:
                print(f"\n📋 {step_name}:")
                print("-" * 40)
                print(step_result['output'])
                print("-" * 40)
                
    def show_current_settings(self):
        """显示当前设置"""
        print("\n⚙️ 当前设置:")
        print(f"股票代码: {self.current_symbol or '未设置'}")
        print(f"市场: {self.current_market or '未设置'}")
        print(f"折现率: {self.discount_rate}")
        print(f"增长率: {self.growth_rate}")
        print(f"总股本: {self.total_shares}")
        
    def show_help(self):
        """显示帮助信息"""
        print("\n📖 帮助信息:")
        print("1. 设置股票代码: 输入股票代码和市场代码")
        print("2. 设置分析参数: 配置折现率、增长率等参数")
        print("3. 运行完整分析: 执行所有分析模块")
        print("4. 运行单项分析: 选择特定分析类型")
        print("5. 查看分析结果: 显示最新的分析报告")
        print("6. 查看当前设置: 显示当前配置的参数")
        print("7. 帮助: 显示此帮助信息")
        print("8. 退出: 退出系统")
        
        print("\n💡 使用提示:")
        print("- 首次使用请先设置股票代码")
        print("- 可以调整分析参数以获得更准确的结果")
        print("- 完整分析需要较长时间，请耐心等待")
        print("- 分析结果会保存，可以重复查看")
        
    async def run(self):
        """运行交互式对话系统"""
        self.print_welcome()
        
        while True:
            try:
                self.print_menu()
                choice = self.get_user_input("请选择操作", "8")
                
                if choice == "1":
                    self.set_stock_symbol()
                elif choice == "2":
                    self.set_analysis_parameters()
                elif choice == "3":
                    await self.run_complete_analysis()
                elif choice == "4":
                    await self.run_single_analysis()
                elif choice == "5":
                    self.show_analysis_results()
                elif choice == "6":
                    self.show_current_settings()
                elif choice == "7":
                    self.show_help()
                elif choice == "8":
                    print("\n👋 感谢使用股票分析智能助手，再见！")
                    break
                else:
                    print("❌ 无效选择，请重新输入")
                    
            except KeyboardInterrupt:
                print("\n\n👋 用户中断，退出系统")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")
                log.error(f"交互式对话系统错误: {e}", exc_info=True)

async def main():
    """主函数"""
    dialogue = InteractiveDialogue()
    await dialogue.run()

if __name__ == "__main__":
    asyncio.run(main()) 