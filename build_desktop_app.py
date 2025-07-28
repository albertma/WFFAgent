#!/usr/bin/env python3
"""
股票分析桌面应用
使用PyQt6构建
"""

import sys
import os
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

from wff_agent.utils import agent_utils

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QLabel, QLineEdit, QComboBox, 
                                QPushButton, QTextEdit, QTabWidget, QGroupBox,
                                QSlider, QSpinBox, QDoubleSpinBox, QMessageBox,
                                QProgressBar, QSplitter)
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
    from PyQt6.QtGui import QFont
except ImportError:
    print("❌ 需要安装PyQt6: pip install PyQt6")
    sys.exit(1)

# 配置日志 - 显示所有日志信息
def setup_logging():
    """设置日志配置"""
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # 创建文件处理器
    file_handler = logging.FileHandler('wff_agent.log', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # 设置特定模块的日志级别
    logging.getLogger('wff_agent').setLevel(logging.INFO)
    logging.getLogger('httpx').setLevel(logging.INFO)
    logging.getLogger('aiohttp').setLevel(logging.INFO)
    logging.getLogger('asyncio').setLevel(logging.INFO)
    
    return logging.getLogger(__name__)

# 初始化日志
log = setup_logging()

class AnalysisWorker(QThread):
    """分析工作线程"""
    progress_updated = pyqtSignal(str, str, str, str)
    analysis_completed = pyqtSignal(dict)
    analysis_failed = pyqtSignal(str)
    
    def __init__(self, analysis_func, *args, **kwargs):
        super().__init__()
        self.analysis_func = analysis_func
        self.args = args
        self.kwargs = kwargs
        
    def run(self):
        try:
            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 创建进度回调函数
            def progress_callback(step_name, message, result, status):
                self.progress_updated.emit(step_name, message, result, status)
            
            # 更新kwargs以包含进度回调
            kwargs = self.kwargs.copy()
            kwargs['progress_callback'] = progress_callback
            
            self.progress_updated.emit("all", "开始分析...", "", "started")
            result = loop.run_until_complete(self.analysis_func(*self.args, **kwargs))
            
            # 确保结果不为None
            if result is None:
                result = {"error": "分析返回空结果"}
            
            self.analysis_completed.emit(result)
            
        except Exception as e:
            import traceback
            error_msg = f"分析失败: {str(e)}\n{traceback.format_exc()}"
            self.analysis_failed.emit(error_msg)
        finally:
            try:
                loop.close()
            except:
                pass

class StockAnalysisApp(QMainWindow):
    """股票分析桌面应用"""
    
    def __init__(self):
        super().__init__()
        self.analysis_results = {}
        self.current_settings = {
            "symbol": "",
            "market": "cn",
            "discount_rate": 0.05,
            "growth_rate": 0.01,
            "total_shares": 0
        }
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("WorkForFun Agent")
        self.setGeometry(100, 100, 1200, 800)
        
        # 设置应用图标
        self.setWindowIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建标题栏
        title_label = QLabel("🤖 投资分析Agent v0.5.0")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # 使用系统默认字体，避免字体加载问题
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(" margin: 5px; padding: 5px;  border-radius: 5px;")
        title_label.setMaximumHeight(50)
        main_layout.addWidget(title_label)
        
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧控制面板
        control_panel = self.create_control_panel()
        splitter.addWidget(control_panel)
        
        # 右侧结果显示面板
        result_panel = self.create_result_panel()
        splitter.addWidget(result_panel)
        
        # 设置分割器比例
        splitter.setSizes([400, 800])
        
        # 状态栏
        self.statusBar().showMessage("就绪")
        
    def create_control_panel(self):
        """创建控制面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 参数设置组
        settings_group = QGroupBox("⚙️ 分析参数设置")
        settings_group.setFont(QFont("Arial", 16))
        settings_layout = QVBoxLayout(settings_group)
        
        # 股票代码输入
        symbol_layout = QHBoxLayout()
        symbol_layout.addWidget(QLabel("股票代码:"))
        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText("例如: 000001, AAPL, 00700")
        symbol_layout.addWidget(self.symbol_input)
        settings_layout.addLayout(symbol_layout)
        
        # 市场选择
        market_layout = QHBoxLayout()
        market_layout.addWidget(QLabel("市场:"))
        self.market_combo = QComboBox()
        self.market_combo.addItems(["cn", "us", "hk"])
        self.market_combo.setToolTip("cn: 中国, us: 美国, hk: 香港")
        market_layout.addWidget(self.market_combo)
        settings_layout.addLayout(market_layout)
        
        # 折现率设置
        discount_layout = QHBoxLayout()
        discount_layout.addWidget(QLabel("折现率:"))
        self.discount_slider = QSlider(Qt.Orientation.Horizontal)
        self.discount_slider.setRange(1, 20)
        self.discount_slider.setValue(5)
        self.discount_slider.setToolTip("用于DCF估值模型")
        discount_layout.addWidget(self.discount_slider)
        self.discount_label = QLabel("5%")
        discount_layout.addWidget(self.discount_label)
        settings_layout.addLayout(discount_layout)
        
        # 增长率设置
        growth_layout = QHBoxLayout()
        growth_layout.addWidget(QLabel("增长率:"))
        self.growth_slider = QSlider(Qt.Orientation.Horizontal)
        self.growth_slider.setRange(0, 10)
        self.growth_slider.setValue(1)
        self.growth_slider.setToolTip("永续增长率")
        growth_layout.addWidget(self.growth_slider)
        self.growth_label = QLabel("1%")
        growth_layout.addWidget(self.growth_label)
        settings_layout.addLayout(growth_layout)
        
        # 总股本设置
        shares_layout = QHBoxLayout()
        shares_layout.addWidget(QLabel("总股本（百万股）:"))
        self.shares_input = QLineEdit()
        self.shares_input.setPlaceholderText("0-99999")
        self.shares_input.setText("0")
        self.shares_input.setToolTip("港股,A股需要填写总股本，取值范围: 0-99999")
        shares_layout.addWidget(self.shares_input)
        settings_layout.addLayout(shares_layout)
        
        layout.addWidget(settings_group)
        
        # 验证按钮
        self.validate_btn = QPushButton("✅ 验证股票代码, 并加载之前分析结果")
        self.validate_btn.clicked.connect(self.validate_symbol)
        self.validate_btn.setFont(QFont("Arial", 16))
        layout.addWidget(self.validate_btn)
        
        # 状态显示
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(60)
        self.status_text.setReadOnly(True)
        self.status_text.setFont(QFont("Arial", 16))
        layout.addWidget(QLabel("验证状态:"))
        layout.addWidget(self.status_text)
        
        # 分析控制组
        analysis_group = QGroupBox("📊 分析控制")
        analysis_layout = QVBoxLayout(analysis_group)
        analysis_group.setFont(QFont("Arial", 16))
        
        
        # 分析按钮
        self.complete_analysis_btn = QPushButton("🚀 运行完整分析")
        self.complete_analysis_btn.clicked.connect(self.run_complete_analysis)
        analysis_layout.addWidget(self.complete_analysis_btn)
        
        self.single_analysis_btn = QPushButton("📈 单项分析")
        self.single_analysis_btn.clicked.connect(self.show_single_analysis_options)
        analysis_layout.addWidget(self.single_analysis_btn)
        
        # 单项分析类型选择
        self.analysis_type_combo = QComboBox()
        self.analysis_type_combo.addItems([
            "ComprehensiveAnalysisAgent",
            "TechAnalysisAgent", 
            "FundamentalAnalysisAgent",
            "NewsAnalysisAgent",
            "GlobalMarketAnalysisAgent"
        ])
        self.analysis_type_combo.setVisible(False)
        analysis_layout.addWidget(self.analysis_type_combo)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        analysis_layout.addWidget(self.progress_bar)
        
        layout.addWidget(analysis_group)
        
        
        # 连接信号
        self.discount_slider.valueChanged.connect(self.update_discount_label)
        self.growth_slider.valueChanged.connect(self.update_growth_label)
        
        layout.addStretch()
        return panel
        
    def create_result_panel(self):
        """创建结果显示面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 结果标签页
        self.result_tabs = QTabWidget()
        self.result_tabs.setFont(QFont("Arial", 16))
        # 综合分析标签页
        self.comprehensive_result = QTextEdit()
        self.comprehensive_result.setReadOnly(True)
        self.comprehensive_result.setStyleSheet("""
            QTextEdit {
                font-family: 'SF Mono', 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                font-size: 16px;
                line-height: 1.4;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        self.result_tabs.addTab(self.comprehensive_result, "📊 综合分析")
        
        # 技术分析标签页
        self.technical_result = QTextEdit()
        self.technical_result.setReadOnly(True)
        self.technical_result.setStyleSheet("""
            QTextEdit {
                font-family: 'SF Mono', 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                font-size: 16px;
                line-height: 1.4;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        self.result_tabs.addTab(self.technical_result, "📈 技术分析")
        
        # 基本面分析标签页
        self.fundamental_result = QTextEdit()
        self.fundamental_result.setReadOnly(True)
        self.fundamental_result.setStyleSheet("""
            QTextEdit {
                font-family: 'SF Mono', 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                font-size: 16px;
                line-height: 1.4;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        self.result_tabs.addTab(self.fundamental_result, "💰 基本面分析")
        
        # 新闻分析标签页
        self.news_result = QTextEdit()
        self.news_result.setReadOnly(True)
        self.news_result.setStyleSheet("""
            QTextEdit {
                font-family: 'SF Mono', 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                font-size: 16px;
                line-height: 1.4;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        self.result_tabs.addTab(self.news_result, "📰 新闻分析")
        
        # 全球市场标签页
        self.global_result = QTextEdit()
        self.global_result.setReadOnly(True)
        self.global_result.setStyleSheet("""
            QTextEdit {
                font-family: 'SF Mono', 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                font-size: 16px;
                line-height: 1.4;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        self.result_tabs.addTab(self.global_result, "🌍 全球市场")
        
        # 设置标签页
        self.settings_display = QTextEdit()
        self.settings_display.setReadOnly(True)
        self.settings_display.setMaximumHeight(200)
        self.settings_display.setStyleSheet("""
            QTextEdit {
                font-family: 'SF Mono', 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                font-size: 16px;
                line-height: 1.4;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        self.result_tabs.addTab(self.settings_display, "⚙️ 当前设置")
        
        # 版本信息标签页
        self.version_display = QTextEdit()
        self.version_display.setReadOnly(True)
        self.version_display.setStyleSheet("""
            QTextEdit {
                font-family: 'SF Mono', 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                font-size: 16px;
                line-height: 1.5;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 15px;
            }
        """)
        self.version_display.setText("""
# 📋 版本信息与更新日志

## 🆕 v0.05 更新内容 (2025-07-28)

### ✨ 新功能
• 新增全球市场分析功能
• 优化股票代码验证机制  
• 改进UI界面设计，提升用户体验
• 在Web界面中添加版本信息显示
• 添加详细的更新日志面板
• 在桌面应用中集成版本信息显示

### 🔧 改进
• 增强数据分析准确性
• 优化内存使用效率
• 修复已知bug和稳定性问题
• 改进错误处理机制
• 优化桌面应用界面布局

### 📊 技术改进
• 升级依赖包版本
• 优化API调用频率
• 改进错误处理机制
• 优化数据缓存机制
• 增强PyQt6桌面应用性能

### 🎯 性能提升
• 分析速度提升约30%
• 减少API调用次数
• 优化数据缓存机制
• 桌面应用启动速度提升

### 📝 文档更新
• 添加详细的版本更新日志
• 更新README文档
• 完善使用说明
• 添加桌面应用使用指南

---

## 📦 应用信息
**版本**: v0.05  
**最新更新**: 2025-07-28  
**支持平台**: Windows, macOS, Linux  
**Python版本**: 3.8+  
**主要技术**: PyQt6, LangChain, Gradio

---

## 🔄 更新历史
### v0.1.0 (2024-12-01)
• 初始版本发布
• 基础股票分析功能
• Web UI界面
• 多种分析代理
• 数据源集成

### v0.5.0 (2025-07-28)
• 当前版本
• 全面功能升级
• 界面优化改进
• 性能显著提升
        """)
        self.result_tabs.addTab(self.version_display, "📋 版本信息")
        
        layout.addWidget(self.result_tabs)
        
        return panel
        
    def update_discount_label(self, value):
        """更新折现率标签"""
        self.discount_label.setText(f"{value}%")
        self.current_settings["discount_rate"] = value / 100.0
        
    def update_growth_label(self, value):
        """更新增长率标签"""
        self.growth_label.setText(f"{value}%")
        self.current_settings["growth_rate"] = value / 100.0
        
    def validate_symbol(self):
        """验证股票代码"""
        symbol = self.symbol_input.text().strip()
        market = self.market_combo.currentText()
        
        log.info(f"🔍 验证股票代码: {symbol} ({market})")
        
        if not symbol:
            self.status_text.setText("❌ 请输入股票代码")
            log.warning("❌ 股票代码为空")
            return
            
        # 简单的股票代码验证
        is_valid = False
        if market == "cn":
            is_valid = len(symbol) == 6 and symbol.isdigit()
        elif market == "us":
            is_valid = symbol.isalpha()
        elif market == "hk":
            is_valid = symbol.isdigit() and len(symbol) == 5
            
        if is_valid:
            self.current_settings["symbol"] = symbol
            self.current_settings["market"] = market
            self.status_text.setText(f"✅ 股票代码 {symbol} ({market}) 验证通过")
            log.info(f"✅ 股票代码验证通过: {symbol} ({market})")
            self.load_analysis_result(symbol, market)
        else:
            self.status_text.setText(f"❌ 股票代码 {symbol} ({market}) 无效")
            log.warning(f"❌ 股票代码无效: {symbol} ({market})")
            
    def validate_total_shares(self):
        """验证总股本输入"""
        shares_text = self.shares_input.text().strip()
        if not shares_text:
            self.current_settings["total_shares"] = 0
            return True
            
        try:
            shares_value = float(shares_text)
            if shares_value < 0 or shares_value > 99999:
                self.status_text.setText("❌ 总股本超出范围 (0-99999)")
                return False
            self.current_settings["total_shares"] = shares_value
            return True
        except ValueError:
            self.status_text.setText("❌ 总股本必须是数字")
            return False
            
    def show_single_analysis_options(self):
        """显示单项分析选项"""
        self.analysis_type_combo.setVisible(True)
        self.analysis_type_combo.currentTextChanged.connect(self.run_single_analysis)
        
    def run_complete_analysis(self):
        """运行完整分析"""
        log.info("🚀 开始运行完整分析...")
        
        if not self.validate_inputs():
            log.warning("❌ 输入验证失败，取消分析")
            return
            
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        
        self.update_settings_display()
        # 创建分析工作线程
        try:
            from wff_agent.agent_client import main as run_agent_analysis
            
            # 获取总股本值
            shares_text = self.shares_input.text().strip()
            total_shares = 0
            if shares_text:
                try:
                    total_shares = int(shares_text)
                except ValueError:
                    total_shares = 0
                    
            log.info(f"📊 分析参数: 股票={self.current_settings['symbol']}, 市场={self.current_settings['market']}, 折现率={self.current_settings['discount_rate']}, 增长率={self.current_settings['growth_rate']}, 总股本={total_shares}百万股")
            
            self.worker = AnalysisWorker(
                run_agent_analysis,
                symbol=self.current_settings["symbol"],
                market=self.current_settings["market"],
                discount_rate=self.current_settings["discount_rate"],
                growth_rate=self.current_settings["growth_rate"],
                total_shares=total_shares*1000000,
                progress_callback=self.update_progress
            )
            
            self.worker.progress_updated.connect(self.update_progress, Qt.ConnectionType.QueuedConnection)
            self.worker.analysis_completed.connect(self.handle_analysis_completed, Qt.ConnectionType.QueuedConnection)
            self.worker.analysis_failed.connect(self.handle_analysis_failed, Qt.ConnectionType.QueuedConnection)
            self.worker.start()
            log.info("✅ 分析工作线程已启动")
            
        except Exception as e:
            log.error(f"❌ 创建分析工作线程失败: {str(e)}")
            self.handle_analysis_failed(str(e))
            
    def run_single_analysis(self, analysis_type):
        """运行单项分析"""
        if not self.validate_inputs():
            return
            
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.update_settings_display()
        try:
            from wff_agent.agent_client import main as run_agent_analysis
            
            # 获取总股本值
            shares_text = self.shares_input.text().strip()
            total_shares = 0
            if shares_text:
                try:
                    total_shares = int(shares_text)
                except ValueError:
                    total_shares = 0
                    
            self.worker = AnalysisWorker(
                run_agent_analysis,
                symbol=self.current_settings["symbol"],
                market=self.current_settings["market"],
                discount_rate=self.current_settings["discount_rate"],
                growth_rate=self.current_settings["growth_rate"],
                total_shares=total_shares*1000000,
                agent_names=[analysis_type]
            )
            
            self.worker.progress_updated.connect(self.update_progress, Qt.ConnectionType.QueuedConnection)
            self.worker.analysis_completed.connect(self.handle_analysis_completed, Qt.ConnectionType.QueuedConnection)
            self.worker.analysis_failed.connect(self.handle_analysis_failed, Qt.ConnectionType.QueuedConnection)
            self.worker.start()
            
        except Exception as e:
            self.handle_analysis_failed(str(e))
            
    def validate_inputs(self):
        """验证输入"""
        if not self.current_settings["symbol"]:
            QMessageBox.warning(self, "警告", "请先设置股票代码")
            return False
            
        # 验证总股本
        if not self.validate_total_shares():
            return False
            
        return True
        
    def update_progress(self, step_name, message, result, status):
        """更新进度"""
        self.statusBar().showMessage(message)
        self._update_step_progress(step_name, result, status)
        
    def _update_step_progress(self, step_name, result, status):
        """更新步骤进度"""
        if status == "started":
            self.progress_bar.setValue(0)
            self.progress_bar.setStyleSheet("background-color: #4CAF50;")
            return
        if status == "completed":
            self.progress_bar.setValue(100)
            if step_name == "ComprehensiveAnalysisAgent":
                self.comprehensive_result.setText(result)
            elif step_name == "TechAnalysisAgent":
                self.technical_result.setText(result)
            elif step_name == "FundamentalAnalysisAgent":
                self.fundamental_result.setText(result)
            elif step_name == "NewsAnalysisAgent":
                self.news_result.setText(result)
            elif step_name == "GlobalMarketAnalysisAgent":
                self.global_result.setText(result)
            self.progress_bar.setStyleSheet("background-color: #4CAF50;")
        elif status == "failed":
            self.progress_bar.setValue(100)
            self.progress_bar.setStyleSheet("background-color: #FF0000;")
        else:
            self.progress_bar.setValue(0)
            
    def handle_analysis_completed(self, result):
        """处理分析完成"""
        self.progress_bar.setVisible(False)
        self.analysis_results = result
        self.update_results_display()
        self.statusBar().showMessage("分析完成")
        
    def handle_analysis_failed(self, error):
        """处理分析失败"""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "错误", f"分析失败: {error}")
        self.statusBar().showMessage("分析失败")
        
    def format_markdown_text(self, text: str) -> str:
        """格式化markdown文本，使其在QTextEdit中更好地显示"""
        if not text:
            return text
            
        # 基本的markdown格式化
        formatted_text = text
        
        # 处理标题
        formatted_text = formatted_text.replace('# ', '\n# ')
        formatted_text = formatted_text.replace('## ', '\n## ')
        formatted_text = formatted_text.replace('### ', '\n### ')
        
        # 处理列表
        formatted_text = formatted_text.replace('\n- ', '\n• ')
        formatted_text = formatted_text.replace('\n* ', '\n• ')
        
        # 处理代码块
        formatted_text = formatted_text.replace('```', '\n```\n')
        
        # 处理表格分隔符
        formatted_text = formatted_text.replace('|', ' | ')
        
        # 添加适当的空行
        formatted_text = formatted_text.replace('\n\n\n', '\n\n')
        
        return formatted_text
    
    def load_analysis_result(self, symbol, market):
        """加载分析结果"""
        report_directory = os.path.join(os.path.dirname(__file__), "reports")
        report_types = ["ComprehensiveAnalysisAgent", 
                        "TechAnalysisAgent", 
                        "FundamentalAnalysisAgent",
                        "NewsAnalysisAgent", 
                        "GlobalMarketAnalysisAgent"]
        for report_type in report_types:
            report_path = os.path.join(report_directory, f"{symbol}_{market}_{report_type}.md")
            log.info(f"加载分析结果: {report_path}")
            result = agent_utils.read_file(report_path)
            if result:
                if 'Comprehensive' in report_type:
                    self.comprehensive_result.setText(result)
                elif 'Tech' in report_type:
                    self.technical_result.setText(result)
                elif 'Fundamental' in report_type:
                    self.fundamental_result.setText(result)
                elif 'News' in report_type:
                    self.news_result.setText(result)
                elif 'Global' in report_type:
                    self.global_result.setText(result)
                
                
                
    def update_results_display(self):
        """更新结果显示"""
        if not self.analysis_results:
            return
            
        # 检查是否有错误
        if isinstance(self.analysis_results, dict) and 'error' in self.analysis_results:
            error_msg = f"分析错误: {self.analysis_results['error']}"
            self.comprehensive_result.setText(error_msg)
            self.technical_result.setText(error_msg)
            self.fundamental_result.setText(error_msg)
            self.news_result.setText(error_msg)
            self.global_result.setText(error_msg)
            return
            
        # 更新各个分析结果
        for agent_name, result in self.analysis_results.items():
            if isinstance(result, dict) and 'output' in result:
                formatted_output = self.format_markdown_text(result['output'])
                if 'Comprehensive' in agent_name:
                    self.comprehensive_result.setText(formatted_output)
                elif 'Tech' in agent_name:
                    self.technical_result.setText(formatted_output)
                elif 'Fundamental' in agent_name:
                    self.fundamental_result.setText(formatted_output)
                elif 'News' in agent_name:
                    self.news_result.setText(formatted_output)
                elif 'Global' in agent_name:
                    self.global_result.setText(formatted_output)
            elif isinstance(result, str):
                # 如果结果是字符串，直接显示
                formatted_result = self.format_markdown_text(result)
                if 'Comprehensive' in agent_name:
                    self.comprehensive_result.setText(formatted_result)
                elif 'Tech' in agent_name:
                    self.technical_result.setText(formatted_result)
                elif 'Fundamental' in agent_name:
                    self.fundamental_result.setText(formatted_result)
                elif 'News' in agent_name:
                    self.news_result.setText(formatted_result)
                elif 'Global' in agent_name:
                    self.global_result.setText(formatted_result)
                    
        # 获取总股本值
        self.update_settings_display()
    
    def update_settings_display(self):
        """更新设置显示"""
        shares_text = int(self.shares_input.text().strip())*1000000
        total_shares_display = shares_text if shares_text else "0"
        settings_text = f"""
当前设置:
股票代码: {self.current_settings['symbol']}
市场: {self.current_settings['market']}
折现率: {self.current_settings['discount_rate']:.1%}
增长率: {self.current_settings['growth_rate']:.1%}
总股本: {total_shares_display}
        """
        self.settings_display.setText(settings_text)

def main():
    """主函数"""
    log.info("🚀 启动股票分析桌面应用 v0.05...")
    
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle('Fusion')
    log.info("✅ 应用样式设置完成")
    
    # 设置字体，避免使用缺失的 Consolas 字体
    font = QFont()
    font.setFamily("SF Pro Display" if sys.platform == "darwin" else "Segoe UI" if sys.platform == "win32" else "DejaVu Sans")
    font.setPointSize(10)
    app.setFont(font)
    log.info("✅ 字体设置完成")
    
    # 创建主窗口
    log.info("📱 创建主窗口...")
    window = StockAnalysisApp()
    window.show()
    log.info("✅ 主窗口显示完成")
    
    log.info("🎯 应用启动完成，进入事件循环")
    # 运行应用
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 