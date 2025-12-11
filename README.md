# 🤖 AI多Agent股票交易分析系统 (增强版)

> 基于LangChain和多Agent协作的智能股票分析系统，采用4层11个Agent架构进行全方位分析

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-green.svg)](https://github.com/langchain-ai/langchain)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌟 项目简介

这是一个创新的股票分析系统，利用多个AI Agent协同工作，从不同维度分析股票投资价值。系统采用**4层架构**，包含**11个专业Agent角色**，能够提供从基本面、技术面、情绪面到新闻面的全方位分析。

### ✨ 核心特性

- 🧠 **4层Agent架构**: 分析师团队 → 研究员辩论 → 交易决策 → 风险管理
- 🆕 **11个专业角色**: 包括基本面、情绪、新闻、技术分析师等
- � **完整新闻分析**: 新闻情感分析、宏观经济指标、事件影响评估
- 🗣️ **智能辩论机制**: 多空双方自动辩论，评分差异触发深度讨论
- ⚖️ **多视角风险评估**: 激进、中立、保守三种投资风格的风险评估
- � **现代化Web界面**: 赛博朋克风格的HTML前端，可部署到Vercel
- 📊 **实时流式输出**: 分析过程可视化，实时展示Agent工作状态

---

## 🏗️ 系统架构

```
📊 Layer 1: Analyst Team (并行分析)
   ├─ 💼 Fundamentals Analyst  - 财务分析、估值评估
   ├─ 💭 Sentiment Analyst     - 社交情绪、市场情绪
   ├─ 📰 News Analyst 🆕       - 新闻情感、宏观经济
   └─ 📈 Technical Analyst     - MACD、RSI、均线系统
              ↓
🗣️ Layer 2: Researcher Team (辩论机制)
   ├─ 📈 Bullish Researcher    - 看涨论证
   ├─ 📉 Bearish Researcher    - 看跌论证
   └─ ⚔️ Debate (评分差异>=阈值时触发)
              ↓
💼 Layer 3: Trader (交易决策)
   └─ 🎯 Trading Decision      - 买入/持有/卖出 + 仓位建议
              ↓
⚖️ Layer 4: Risk Management + Portfolio Manager
   ├─ 🔥 Aggressive Risk       - 激进派评估
   ├─ ⚖️ Neutral Risk          - 中立派评估
   ├─ 🛡️ Conservative Risk     - 保守派评估
   └─ 👔 Portfolio Manager     - 最终决策
```

---

## 🚀 快速开始

### 1. 环境准备

**系统要求:**
- Python 3.9+
- pip 或 conda

**克隆项目:**
```bash
git clone https://github.com/yourusername/langChainAgent.git
cd langChainAgent
```

**安装依赖:**
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

**配置API密钥:**
```bash
# 创建.env文件
cp .env.example .env

# 编辑.env文件，添加你的API密钥
# api-key=your_api_key_here
# base-url=https://api.siliconflow.cn/v1
```

### 2. 启动方式

#### 方式一：命令行版 (CLI)

**增强版系统 (推荐):**
```bash
source venv/bin/activate
python app_multi_agent_enhanced.py

# 或直接分析指定股票
python app_multi_agent_enhanced.py --symbol 600519

# 调整辩论阈值
python app_multi_agent_enhanced.py --symbol 600519 --threshold 2.0 --max-rounds 3
```

**经典版系统 (快速):**
```bash
python app_multi_agent.py
```

#### 方式二：Web界面 (Vercel)

**本地测试:**
```bash
cd vercel_app/api
source ../../venv/bin/activate
python index.py
```

然后访问: http://localhost:8000

**部署到Vercel:**
1. 推送代码到GitHub
2. 在Vercel导入项目
3. 设置Root Directory为 `vercel_app`
4. 部署

详见: [VERCEL_DEPLOYMENT.md](file:///Users/haoyin/.gemini/antigravity/brain/6f4e44d9-e910-42b0-862d-c121f1d16ebf/VERCEL_DEPLOYMENT.md)

---

## 📖 使用示例

### CLI示例

```bash
# 分析贵州茅台 (600519)
python app_multi_agent_enhanced.py --symbol 600519

# 输出示例:
================================================================================
           🚀 增强版多Agent股票交易分析系统
================================================================================

系统架构 (4层):
  📊 第1层: 分析师团队
      1️⃣  基本面分析师 - 财务健康度、估值分析
      2️⃣  情绪分析师 - 社交媒体情绪、市场情绪
      3️⃣  新闻分析师 - 新闻事件、宏观经济 🆕
      4️⃣  技术分析师 - MACD、RSI、均线系统
  ...
```

### API调用示例

```python
from src.agent.multi_agent_system_enhanced import EnhancedMultiAgentSystem

# 初始化系统
system = EnhancedMultiAgentSystem(
    model="Qwen/Qwen2.5-7B-Instruct",
    api_key="your_api_key",
    debate_threshold=3.0
)

# 运行分析
result = system.run_analysis("600519", verbose=True)

# 访问结果
print(f"最终建议: {result.final_decision.recommendation}")
print(f"信心水平: {result.final_decision.confidence}")
print(f"仓位建议: {result.final_decision.position_suggestions}")
```

---

## 🛠️ 技术栈

| 技术 | 用途 |
|------|------|
| **LangChain** | Agent框架和工具编排 |
| **LangChain-OpenAI** | LLM接口集成 |
| **AkShare** | A股数据获取 |
| **FastAPI** | Web API服务 |
| **HTML/CSS/JS** | 现代化前端界面 |
| **Uvicorn** | ASGI服务器 |

---

## 📊 分析工具

### 技术分析工具
- `get_stock_history` - 历史行情数据
- `get_stock_technical_indicators` - 技术指标 (MA, MACD, RSI)
- `get_industry_comparison` - 行业对比

### 基本面分析工具 🆕
- `get_company_financials` - 公司财务数据
- `calculate_intrinsic_value` - 内在价值评估
- `get_performance_metrics` - 业绩指标
- `identify_red_flags` - 财务风险识别

### 情绪分析工具 🆕
- `analyze_social_media_sentiment` - 社交媒体情绪
- `get_public_sentiment_score` - 公众情绪评分
- `track_market_mood` - 市场情绪追踪

### 新闻分析工具 🆕
- `analyze_news_sentiment` - 新闻情感分析
- `get_macroeconomic_indicators` - 宏观经济指标
- `assess_event_impact` - 事件影响评估
- `get_global_market_news` - 全球市场新闻

---

## 📂 项目结构

```
langChainAgent/
├── src/
│   ├── agent/
│   │   ├── multi_agent_system_enhanced.py  🆕 增强版4层系统
│   │   ├── agent_prompts_enhanced.py       🆕 11个Agent提示词
│   │   ├── multi_agent_system.py           经典版5Agent系统
│   │   └── agent_prompts.py                经典版提示词
│   └── tools/
│       ├── news_analysis_tools.py          🆕 新闻分析工具
│       ├── sentiment_tools.py              🆕 情绪分析工具
│       ├── fundamentals_tools.py           🆕 基本面分析工具
│       └── stock_data.py                   技术分析工具
├── vercel_app/                             🆕 Vercel部署版本
│   ├── api/
│   │   └── index.py                        FastAPI服务
│   ├── public/
│   │   ├── index.html                      现代化HTML界面
│   │   ├── script.js                       前端逻辑
│   │   └── style.css                       赛博朋克风格
│   ├── requirements.txt
│   └── vercel.json
├── app_multi_agent_enhanced.py             🆕 增强版CLI入口
├── app_multi_agent.py                      经典版CLI入口
└── README.md

```

---

## � 版本对比

| 特性 | 经典版 | 增强版 🆕 |
|------|--------|----------|
| Agent数量 | 5个 | **11个** |
| 架构层级 | 扁平 | **4层** |
| News Analyst | 基础 | **完整实现** |
| 风险评估 | 无 | **3个视角** |
| 技术指标 | MA均线 | **MA+MACD+RSI** |
| 分析维度 | 2维 | **4维** |
| 分析时间 | ~30秒 | ~1-2分钟 |
| 适用场景 | 快速决策 | 重要投资决策 |

---

## ⚙️ 配置选项

### 命令行参数

```bash
python app_multi_agent_enhanced.py \
  --symbol 600519 \              # 股票代码
  --threshold 3.0 \              # 辩论触发阈值
  --max-rounds 2 \               # 最大辩论轮次
  --no-verbose                   # 静默模式
```

### 环境变量

```bash
# .env文件
api-key=your_silicon_flow_api_key
base-url=https://api.siliconflow.cn/v1
```

---

## 📚 相关文档

- [快速开始指南](file:///Users/haoyin/.gemini/antigravity/brain/6f4e44d9-e910-42b0-862d-c121f1d16ebf/ENHANCED_QUICK_START.md)
- [Vercel部署指南](file:///Users/haoyin/.gemini/antigravity/brain/6f4e44d9-e910-42b0-862d-c121f1d16ebf/VERCEL_DEPLOYMENT.md)
- [系统架构详解](file:///Users/haoyin/.gemini/antigravity/brain/6f4e44d9-e910-42b0-862d-c121f1d16ebf/walkthrough.md)

---

## ⚠️ 免责声明

**本系统仅用于教育和研究目的，不构成任何投资建议。**

- 📊 分析结果基于历史数据和AI模型推理
- ⚡ 市场瞬息万变，过往表现不代表未来
- 💰 股市有风险，投资需谨慎
- 🎯 请独立思考，理性决策

---

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain) - Agent框架
- [AkShare](https://github.com/akfamily/akshare) - 金融数据接口
- [FastAPI](https://fastapi.tiangolo.com/) - Web框架
- [Vercel](https://vercel.com/) - 部署平台

---

## 📮 联系方式

- 项目主页: https://github.com/yourusername/langChainAgent
- Issue追踪: https://github.com/yourusername/langChainAgent/issues
- 讨论区: https://github.com/yourusername/langChainAgent/discussions

---

<p align="center">
  <strong>Made with ❤️ using LangChain & Multi-Agent AI</strong><br>
  如果这个项目对你有帮助，请给一个 ⭐ Star!
</p>
