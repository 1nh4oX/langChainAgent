# 🤖 AI Multi-Agent Stock Analysis System

> An AI-powered stock analysis system built on LangChain. Four layers and eleven agents collaborate to deliver end-to-end investment research.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-green.svg)](https://python.langchain.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Highlights

- 🧠 **Four-layer AI stack**: Analyst squad → Researcher debate → Trading decision → Risk oversight
- 🤖 **11 specialized agents**: Fundamentals, sentiment, news, technicals + bull/bear debate + risk reviewers
- 🗣️ **Autonomous debate**: Bulls and bears argue automatically; score gaps trigger deeper rounds
- 📊 **Streaming output**: Visualize each agent’s live reasoning and status
- 🎨 **Modern UI**: React front end + FastAPI back end

## 🏗️ Architecture

```
📊 Layer 1: Analyst squad (parallel)
   ├─ 💼 Fundamentals analyst – financial health, valuation
   ├─ 💭 Sentiment analyst – social and market mood
   ├─ 📰 News analyst – news tone, macro signals
   └─ 📈 Technical analyst – MACD, RSI, moving averages
            ↓
🗣️ Layer 2: Research team (debate)
   ├─ 📈 Bull researcher – long thesis
   ├─ 📉 Bear researcher – short thesis
   └─ ⚔️ Auto-debate (fires when score delta ≥ threshold)
            ↓
💼 Layer 3: Trader (decisioning)
   └─ 🎯 Trade decision – buy/hold/sell + sizing guidance
            ↓
⚖️ Layer 4: Risk management (multi-lens)
   ├─ 🔥 Aggressive review
   ├─ ⚖️ Neutral review
   ├─ 🛡️ Conservative review
   └─ 👔 Portfolio manager – final call
```

## 🚀 Quick Start

### Environment

```bash
# 1. Clone
git clone https://github.com/yourusername/langChainAgent.git
cd langChainAgent

# 2. Create venv and install deps
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure API keys
cp .env.example .env
# Edit .env and add your API key(s)
```

### Run Options

#### Option 1: LAN deployment (recommended)

One-click script:

```bash
./start_lan.sh
```

The script will:
- ✅ Detect your LAN IP
- ✅ Start the back end (port 8000)
- ✅ Start the front end (port 5173)
- ✅ Print the access URL

**LAN access**: Devices on the same Wi-Fi open `http://<your-ip>:5173`

More details: [LAN_DEPLOY.md](LAN_DEPLOY.md)

#### Option 2: Local dev & test

**Back end**:
```bash
cd api
python3 main.py
# Visit http://localhost:8000/docs for the API docs
```

**Front end** (new terminal):
```bash
cd frontend
npm install  # first time only
npm run dev
# Visit http://localhost:5173
```

More details: [LOCAL_TEST_GUIDE.md](LOCAL_TEST_GUIDE.md)

#### Option 3: CLI mode

```bash
# Interactive mode
python app_multi_agent_enhanced.py

# Analyze a specific ticker
python app_multi_agent_enhanced.py --symbol 600519

# Customize parameters
python app_multi_agent_enhanced.py --symbol 600519 --threshold 2.0 --max-rounds 3
```

## 📖 Usage Examples

### Web UI

1. Open the front-end URL in your browser.
2. Enter a 6-digit ticker (e.g., 600519).
3. Open ⚙️ Settings to configure API key and model.
4. Click the → button to start.
5. Watch the four-layer agent results in real time.

### API

```python
from src.agent.multi_agent_system_enhanced import EnhancedMultiAgentSystem

# Initialize
system = EnhancedMultiAgentSystem(
    model="Qwen/Qwen2.5-7B-Instruct",
    api_key="your_api_key",
    base_url="https://api.siliconflow.cn/v1",
    debate_threshold=3.0
)

# Run analysis
result = system.run_analysis("600519", verbose=True)

# Inspect output
print(f"Final recommendation: {result.final_decision.recommendation}")
print(f"Confidence: {result.final_decision.confidence}")
print(f"Position sizing: {result.final_decision.position_suggestions}")
```

## 🛠️ Tech Stack

| Tech | Purpose |
|------|---------|
| **LangChain** | Agent framework and tool orchestration |
| **React** | Front-end UI |
| **FastAPI** | Back-end APIs |
| **AkShare** | China A-share market data |
| **react-markdown** | Markdown rendering |

## 📂 Project Layout

```
langChainAgent/
├── frontend/                    # React front end
│   └── src/App.jsx             # App entry
├── api/                         # FastAPI back end
│   └── main.py                 # API entry
├── src/
│   ├── agent/                  # Four-layer, 11-agent system
│   │   ├── multi_agent_system_enhanced.py
│   │   └── agent_prompts_enhanced.py
│   └── tools/                  # Data and analysis helpers
│       ├── stock_data.py
│       ├── fundamentals_tools.py
│       ├── sentiment_tools.py
│       └── news_analysis_tools.py
├── app_multi_agent_enhanced.py  # CLI entry
├── start_lan.sh                 # One-click LAN start
├── requirements.txt             # Python deps
└── 文档/
    ├── README.md               # Project overview
    ├── LOCAL_TEST_GUIDE.md     # Local testing guide
    └── LAN_DEPLOY.md           # LAN deployment guide
```

## ⚙️ Configuration

### CLI Arguments

```bash
--symbol       Stock ticker (6 digits)
--threshold    Debate trigger threshold (default: 3.0)
--max-rounds   Max debate rounds (default: 2)
--no-verbose   Quiet mode
```

### Environment Variables

```bash
# .env
api-key=your_api_key_here
base-url=https://api.siliconflow.cn/v1
```

## ⚠️ Disclaimer

**For education and research only. This is not investment advice.**

- 📊 Results rely on historical data and AI reasoning.
- ⚡ Markets change quickly; past performance is not indicative of future results.
- 💰 Investing carries risk; proceed with caution.
- 🎯 Make independent, rational decisions.

## 📄 License

Released under the MIT License – see [LICENSE](LICENSE).

## 🙏 Credits

- [LangChain](https://github.com/langchain-ai/langchain) – agent framework
- [AkShare](https://github.com/akfamily/akshare) – financial data API
- [FastAPI](https://fastapi.tiangolo.com/) – web framework

---

<p align="center">
  <strong>Made with ❤️ using LangChain & Multi-Agent AI</strong><br>
  If this project helps you, please drop a ⭐
</p>
