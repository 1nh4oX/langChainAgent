# 🤖 AI多Agent股票分析系统

> 基于LangChain的智能股票分析系统，采用4层11个AI Agent协同工作，提供全方位投资分析

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-green.svg)](https://python.langchain.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ 核心特性

- 🧠 **4层AI架构**: 分析师团队 → 研究员辩论 → 交易决策 → 风险管理
- 🤖 **11个专业Agent**: 基本面、情绪、新闻、技术分析 + 多空辩论 + 风险评估
- 🗣️ **智能辩论机制**: 多空双方自动辩论，分歧触发深度讨论
- 📊 **实时流式输出**: 可视化分析过程，展示每个Agent的工作状态
- 🎨 **现代化界面**: React前端 + FastAPI后端

## 🏗️ 系统架构

```
📊 Layer 1: 分析师团队 (并行分析)
   ├─ 💼 基本面分析师 - 财务健康度、估值评估
   ├─ 💭 情绪分析师 - 社交媒体、市场情绪
   ├─ 📰 新闻分析师 - 新闻情感、宏观经济
   └─ 📈 技术分析师 - MACD、RSI、均线系统
            ↓
🗣️ Layer 2: 研究员团队 (辩论机制)
   ├─ 📈 看涨研究员 - 多头论证
   ├─ 📉 看跌研究员 - 空头论证
   └─ ⚔️ 自动辩论 (评分差异≥阈值时触发)
            ↓
💼 Layer 3: 交易员 (决策制定)
   └─ 🎯 交易决策 - 买入/持有/卖出 + 仓位建议
            ↓
⚖️ Layer 4: 风险管理 (多视角评估)
   ├─ 🔥 激进派评估
   ├─ ⚖️ 中立派评估
   ├─ 🛡️ 保守派评估
   └─ 👔 投资组合经理 - 最终决策
```

## 🚀 快速开始

### 环境准备

```bash
# 1. 克隆项目
git clone https://github.com/yourusername/langChainAgent.git
cd langChainAgent

# 2. 创建虚拟环境并安装依赖
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. 配置API密钥
cp .env.example .env
# 编辑 .env 文件，添加你的 API Key
```

### 启动方式

#### 方式一：局域网部署（推荐）

使用一键启动脚本：

```bash
./start_lan.sh
```

脚本会自动：
- ✅ 检测局域网IP
- ✅ 启动后端服务 (端口8000)
- ✅ 启动前端界面 (端口5173)
- ✅ 显示访问地址

**局域网访问**: 同一WiFi下的设备访问 `http://你的IP:5173`

📖 详细说明: [LAN_DEPLOY.md](LAN_DEPLOY.md)

#### 方式二：本地开发测试

**启动后端**:
```bash
cd api
python3 main.py
# 访问 http://localhost:8000/docs 查看API文档
```

**启动前端**（新终端）:
```bash
cd frontend
npm install  # 首次需要
npm run dev
# 访问 http://localhost:5173
```

📖 详细说明: [LOCAL_TEST_GUIDE.md](LOCAL_TEST_GUIDE.md)

#### 方式三：命令行版本

```bash
# 交互式分析
python app_multi_agent_enhanced.py

# 直接分析指定股票
python app_multi_agent_enhanced.py --symbol 600519

# 自定义参数
python app_multi_agent_enhanced.py --symbol 600519 --threshold 2.0 --max-rounds 3
```

## 📖 使用示例

### Web界面使用

1. 打开浏览器访问前端地址
2. 输入6位股票代码 (如: 600519)
3. 点击⚙️设置，配置API Key和模型
4. 点击→按钮开始分析
5. 实时查看4层Agent分析结果

### API调用示例

```python
from src.agent.multi_agent_system_enhanced import EnhancedMultiAgentSystem

# 初始化系统
system = EnhancedMultiAgentSystem(
    model="Qwen/Qwen2.5-7B-Instruct",
    api_key="your_api_key",
    base_url="https://api.siliconflow.cn/v1",
    debate_threshold=3.0
)

# 运行分析
result = system.run_analysis("600519", verbose=True)

# 查看结果
print(f"最终建议: {result.final_decision.recommendation}")
print(f"信心水平: {result.final_decision.confidence}")
print(f"仓位建议: {result.final_decision.position_suggestions}")
```

## 🛠️ 技术栈

| 技术 | 用途 |
|------|------|
| **LangChain** | AI Agent框架和工具编排 |
| **React** | 前端界面 |
| **FastAPI** | 后端API服务 |
| **AkShare** | A股数据获取 |
| **react-markdown** | Markdown渲染 |

## 📂 项目结构

```
langChainAgent/
├── frontend/                    # React前端
│   └── src/App.jsx             # 主应用
├── api/                         # FastAPI后端
│   └── main.py                 # API入口
├── src/
│   ├── agent/                  # 4层11个Agent系统
│   │   ├── multi_agent_system_enhanced.py
│   │   └── agent_prompts_enhanced.py
│   └── tools/                  # 数据分析工具
│       ├── stock_data.py
│       ├── fundamentals_tools.py
│       ├── sentiment_tools.py
│       └── news_analysis_tools.py
├── app_multi_agent_enhanced.py  # CLI入口
├── start_lan.sh                 # 局域网一键启动
├── requirements.txt             # Python依赖
└── 文档/
    ├── README.md               # 项目说明
    ├── LOCAL_TEST_GUIDE.md     # 本地测试指南
    └── LAN_DEPLOY.md           # 局域网部署指南
```

## ⚙️ 配置选项

### 命令行参数

```bash
--symbol    股票代码 (6位数字)
--threshold 辩论触发阈值 (默认: 3.0)
--max-rounds 最大辩论轮次 (默认: 2)
--no-verbose 静默模式
```

### 环境变量

```bash
# .env 文件
api-key=your_api_key_here
base-url=https://api.siliconflow.cn/v1
```

## ⚠️ 免责声明

**本系统仅用于教育和研究目的，不构成任何投资建议。**

- 📊 分析结果基于历史数据和AI模型推理
- ⚡ 市场瞬息万变，过往表现不代表未来
- 💰 股市有风险，投资需谨慎
- 🎯 请独立思考，理性决策

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain) - Agent框架
- [AkShare](https://github.com/akfamily/akshare) - 金融数据接口
- [FastAPI](https://fastapi.tiangolo.com/) - Web框架

---

<p align="center">
  <strong>Made with ❤️ using LangChain & Multi-Agent AI</strong><br>
  如果这个项目对你有帮助，请给一个 ⭐ Star!
</p>
