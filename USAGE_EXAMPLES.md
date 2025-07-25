# WFF Agent 使用示例

## 🚀 快速开始

### 1. 桌面应用使用示例

```bash
# 启动桌面应用
python build_desktop_app.py
```

**使用步骤：**
1. 输入股票代码（如：AAPL、000001、00700）
2. 选择市场（cn/us/hk）
3. 调整折现率和增长率参数
4. 点击"验证股票代码"按钮
5. 选择分析类型（完整分析或单项分析）
6. 等待分析完成，查看结果

### 2. Web UI 使用示例

```bash
# 启动 Web UI
streamlit run src/wff_agent/web_ui.py
```

**功能特点：**
- 实时数据更新
- 交互式图表
- 多标签页展示
- 响应式设计

### 3. 命令行使用示例

```bash
# 启动交互式命令行
python -m src.wff_agent.interactive_dialogue
```

**交互流程：**
```
🤖 欢迎使用股票分析智能助手！

请选择操作：
1. 设置股票代码
2. 设置分析参数
3. 运行完整分析
4. 运行单项分析
5. 显示当前设置
6. 显示帮助信息
0. 退出

请输入选择 (0-6): 1
```

## 📊 分析类型详解

### 1. 综合分析 (ComprehensiveAnalysisAgent)

**适用场景：** 需要全面了解股票的投资价值

**分析内容：**
- 多因子权重分配（技术面50%、基本面30%、市场情绪20%）
- 蒙特卡洛模拟（10,000次随机游走）
- 风险收益比计算
- 操作建议生成

**示例输出：**
```
### 综合决策报告：苹果公司（AAPL）

#### 多因子权重分配
| 因子类别 | 权重 | 子因子 | 权重 |
|---------|------|--------|------|
| 技术面   | 50%  | 趋势   | 30%  |
|          |      | 动量   | 20%  |
| 基本面   | 30%  | 估值   | 20%  |
|          |      | 质量   | 10%  |
| 市场情绪 | 20%  | -      | -    |

#### 蒙特卡洛模拟结果
- 上涨概率：65%
- 下跌概率：25%
- 震荡概率：10%

#### 操作建议
- 短期投资者：可考虑买入，止损位 $150
- 长期投资者：持有，关注新产品发布
```

### 2. 技术分析 (TechAnalysisAgent)

**适用场景：** 关注短期交易机会

**分析内容：**
- 趋势分析（移动平均线、趋势线）
- 动量指标（MACD、RSI、KDJ）
- 支撑阻力位识别
- 技术形态识别

**示例输出：**
```
### 技术分析报告：特斯拉（TSLA）

#### 趋势分析
- 短期趋势：上升
- 中期趋势：震荡
- 长期趋势：上升

#### 关键指标
- MACD：金叉形成，买入信号
- RSI：65，中性偏强
- 布林带：股价位于上轨附近

#### 支撑阻力位
- 支撑位：$180
- 阻力位：$220
- 关键价位：$200

#### 操作建议
- 突破 $220 可加仓
- 跌破 $180 止损
```

### 3. 基本面分析 (FundamentalAnalysisAgent)

**适用场景：** 价值投资，长期持有

**分析内容：**
- 财务指标计算（ROE、ROA、毛利率等）
- DCF 估值模型
- 自由现金流分析
- 估值比率分析

**示例输出：**
```
### 基本面分析报告：微软（MSFT）

#### 财务指标
- ROE：35.2%
- ROA：15.8%
- 毛利率：68.5%
- 净利率：36.2%

#### 估值分析
- 市盈率（PE）：28.5
- 市净率（PB）：12.3
- 市销率（PS）：11.2

#### DCF 估值
- 内在价值：$380
- 当前价格：$350
- 安全边际：8.6%

#### 投资建议
- 估值合理，可考虑买入
- 关注云计算业务增长
```

### 4. 新闻情绪分析 (NewsAnalysisAgent)

**适用场景：** 了解市场情绪和事件影响

**分析内容：**
- 实时新闻监控
- 情绪分析（正面/负面/中性）
- 事件影响评估
- 市场反应预测

**示例输出：**
```
### 新闻情绪分析报告：阿里巴巴（BABA）

#### 新闻统计
- 正面新闻：15条
- 负面新闻：8条
- 中性新闻：12条
- 情绪指数：0.45（偏正面）

#### 热点事件
1. 云计算业务增长超预期（正面）
2. 电商市场份额提升（正面）
3. 监管政策变化（负面）

#### 市场影响
- 短期影响：偏正面
- 中期影响：中性
- 长期影响：偏正面

#### 建议
- 关注监管政策变化
- 云计算业务值得关注
```

### 5. 全球市场分析 (GlobalMarketAnalysisAgent)

**适用场景：** 了解宏观经济环境

**分析内容：**
- 宏观经济指标
- 全球市场趋势
- 汇率影响分析
- 地缘政治风险

**示例输出：**
```
### 全球市场分析报告

#### 宏观经济指标
- 美国 CPI：3.2%（环比下降）
- 美联储利率：5.25%
- 美元指数：102.5
- 原油价格：$75/桶

#### 全球市场趋势
- 美股：震荡上行
- 欧股：小幅上涨
- 亚太：分化明显
- 新兴市场：资金流入

#### 汇率影响
- 人民币汇率：7.15
- 欧元汇率：1.08
- 日元汇率：150

#### 风险提示
- 地缘政治风险上升
- 通胀压力仍存
- 央行政策不确定性
```

## 🔧 高级功能

### 1. 自定义参数

```python
# 在桌面应用中调整参数
discount_rate = 0.08  # 折现率
growth_rate = 0.03    # 增长率
total_shares = 1000000000  # 总股本
```

### 2. 批量分析

```python
# 可以同时分析多只股票
symbols = ["AAPL", "MSFT", "GOOGL"]
markets = ["us", "us", "us"]

for symbol, market in zip(symbols, markets):
    # 运行分析
    result = await run_agent(symbol, market, 0.08, 0.03)
```

### 3. 历史数据对比

```python
# 比较不同时期的分析结果
# 系统会自动保存历史分析结果
# 可以在桌面应用中加载历史结果
```

## ⚠️ 注意事项

1. **API 限制**：某些数据源有调用频率限制
2. **数据延迟**：实时数据可能有 15-20 分钟延迟
3. **分析准确性**：AI 分析结果仅供参考，不构成投资建议
4. **风险提示**：投资有风险，请根据个人情况谨慎决策

## 🆘 常见问题

### Q: 如何获取 API 密钥？
A: 
- News API: https://newsapi.org/
- Alpha Vantage: https://www.alphavantage.co/
- DeepSeek: https://platform.deepseek.com/

### Q: 分析结果不准确怎么办？
A: 
- 检查股票代码是否正确
- 确认市场选择是否正确
- 调整分析参数
- 查看数据源是否正常

### Q: 程序运行缓慢怎么办？
A: 
- 检查网络连接
- 确认 API 密钥有效
- 关闭不必要的程序
- 考虑使用单项分析而非完整分析

### Q: 如何保存分析结果？
A: 
- 桌面应用会自动保存到 reports/ 目录
- 可以手动复制结果文本
- 支持导出为 Markdown 格式 