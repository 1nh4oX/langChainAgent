# 🤖 Stock Analysis Agent

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/LangChain-0.1+-green.svg" alt="LangChain">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/Status-Active-success.svg" alt="Status">
</p>

基于 LangChain 的智能 A 股股票分析系统，支持历史数据查询、新闻资讯获取、技术指标分析等多项功能。

## ✨ 核心功能

- 📊 **历史行情查询** - 获取股票历史价格、成交量数据
- 📰 **新闻资讯采集** - 实时获取股票相关新闻报道
- 📈 **技术指标分析** - 计算MA5/MA10/MA20均线、涨跌幅等
- 🏢 **行业对比分析** - 查询基本面信息、行业地位、估值水平
- 🎯 **综合智能分析** - 多维度整合分析，提供投资参考

## 📁 项目结构

```
stock-analysis-agent/
├── src/                      # 源代码
│   ├── agent/                # Agent 核心模块
│   ├── tools/                # 工具模块（5个分析工具）
│   ├── config/               # 配置管理
│   └── utils/                # 工具函数
├── scripts/                  # 脚本工具
├── tests/                    # 测试代码
├── data/                     # 数据目录
├── docs/                     # 文档
├── examples/                 # 示例代码
├── ui/                       # UI界面（预留）
├── app.py                    # 主程序入口
├── requirements.txt          # 依赖配置
└── README.md                 # 本文件
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API

复制 `.env.example` 为 `.env` 并填入你的 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
api-key=your-api-key-here
base-url=https://api.siliconflow.cn/v1
model=Qwen/Qwen2.5-7B-Instruct
```

**免费 API 推荐：**
- [硅基流动](https://siliconflow.cn) - 免费 2000万 tokens ⭐
- [智谱AI](https://open.bigmodel.cn) - 免费 1000万 tokens
- [月之暗面](https://platform.moonshot.cn) - 少量免费额度

### 3. 运行程序

```bash
# 交互式运行
python app.py

# 采集新闻数据
python scripts/collect_news.py

# 运行示例
python examples/basic_usage.py
```

## 📖 使用示例

### 基础使用

```python
from src.agent import StockAnalysisAgent

# 初始化 Agent
agent = StockAnalysisAgent()

# 运行查询
result = agent.run("分析一下贵州茅台（600519）的最近走势")

# 输出结果
print(result['output'])
print(f"迭代次数: {result['iterations']}")
```

### 添加自定义工具

```python
from langchain_core.tools import tool
from src.agent import StockAnalysisAgent

# 定义自定义工具
@tool
def my_custom_tool(param: str) -> str:
    """工具描述"""
    return "result"

# 添加到 Agent
agent = StockAnalysisAgent()
agent.add_tool(my_custom_tool)
```

### 批量分析

```python
from src.agent import StockAnalysisAgent

agent = StockAnalysisAgent()

stocks = ["600519", "000001", "600036"]
for stock in stocks:
    result = agent.run(f"分析股票代码 {stock}")
    print(f"\n{stock} 分析结果:")
    print(result['output'])
```

## 🛠️ 开发指南

### 添加新工具

1. 在 `src/tools/` 创建新的工具文件
2. 使用 `@tool` 装饰器定义工具
3. 在 `src/tools/__init__.py` 导出工具
4. 在 Agent 中注册工具

示例：

```python
# src/tools/my_tools.py
from langchain_core.tools import tool

@tool
def get_financial_report(symbol: str) -> str:
    """获取财务报表"""
    # 实现逻辑
    return "财务数据"
```

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_agent.py
```

## 🎨 UI 界面（规划中）

我们计划开发以下界面：

- [ ] **Streamlit Web UI** - 交互式 Web 界面
- [ ] **Gradio UI** - 快速原型界面
- [ ] **Flask API** - RESTful API 服务
- [ ] **数据可视化** - K线图、指标图表

## 🤝 贡献指南

我们欢迎所有形式的贡献！详见 [CONTRIBUTING.md](CONTRIBUTING.md)

### 贡献流程

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 文档

- [API 文档](docs/API.md) - 完整的 API 说明
- [项目结构](docs/PROJECT_STRUCTURE.md) - 目录结构和模块职责
- [更新日志](docs/CHANGELOG.md) - 版本更新历史
- [迁移指南](MIGRATION_GUIDE.md) - 新旧版本对比

## 📊 工具列表

| 工具 | 功能 | 数据源 |
|------|------|--------|
| `get_stock_history` | 获取历史行情 | AkShare |
| `get_stock_news` | 获取新闻资讯 | AkShare |
| `get_stock_technical_indicators` | 计算技术指标 | AkShare |
| `get_industry_comparison` | 行业对比 | AkShare |
| `analyze_stock_comprehensive` | 综合分析 | AkShare |

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## ⚠️ 免责声明

本系统仅用于学习和研究目的，不构成任何投资建议。股市有风险，投资需谨慎。

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain) - Agent 框架
- [AkShare](https://github.com/akfamily/akshare) - 金融数据接口
- [OpenAI](https://openai.com/) - GPT 模型
- 所有贡献者

## 📮 联系方式

- 项目主页: https://github.com/yourusername/stock-analysis-agent
- Issue 追踪: https://github.com/yourusername/stock-analysis-agent/issues

## ⭐ Star History

如果这个项目对你有帮助，请给我们一个 Star ⭐

---

<p align="center">Made with ❤️ by Stock Analysis Agent Team</p>
