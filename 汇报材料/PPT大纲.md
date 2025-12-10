# 智能股票分析 Agent 技术汇报

## PPT 大纲（3-5分钟）- 逻辑顺序版（7页）

---

### 第1页：标题页（10秒）
**智能股票分析 Agent**  
基于 LangChain 的 A 股分析系统

- 汇报人：[你的名字]
- 汇报时间：3-5分钟
- 核心内容：架构 + 代码实现

---

### 第2页：系统架构 - 整体流程（40秒）

**完整执行流程：**

```
用户查询
    ↓
Streamlit UI（前端展示）
    ↓
Agent 初始化（绑定工具 + 提示词）
    ↓
Agent 循环执行（ReAct模式）
    ↓
工具调用（获取真实数据）
    ↓
数据返回 → AI 分析 → 输出报告
```

**三层架构：**
1. **展示层** - Streamlit Web UI（API配置 + 交互界面）
2. **Agent层** - LangChain Agent（决策 + 工具调度）
3. **工具层** - 5个股票分析工具（AkShare数据）

**核心思想：** Agent 作为"大脑"，工具作为"手脚"，协同完成分析任务

---

### 第3页：工具实现 - Tools的实现与作用（80秒）⭐⭐⭐

**完整工具代码示例：**

```python
from langchain_core.tools import tool
import akshare as ak
import pandas as pd

@tool  # LangChain 装饰器：自动生成工具描述
def get_stock_history(symbol: str) -> str:
    """
    获取中国A股股票的近期历史行情数据。
    
    Args:
        symbol: 股票代码（6位数字，如 '600519' 贵州茅台）
    
    Returns:
        包含日期、开盘、收盘、最高、最低、成交量的表格
    """
    try:
        # 1. 调用 AkShare API
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        end_date = datetime.now().strftime("%Y%m%d")
        
        df = ak.stock_zh_a_hist(
            symbol=symbol,         # 股票代码
            period="daily",        # 日线数据
            start_date=start_date, # 开始日期
            end_date=end_date,     # 结束日期
            adjust="qfq"           # 前复权
        )
        
        # 2. 数据清洗（只保留关键字段和最近10天）
        df = df[['日期', '开盘', '收盘', '最高', '最低', '成交量']]
        recent_data = df.tail(10).copy()
        
        # 3. 返回 Markdown 表格（LLM 易于理解）
        return recent_data.to_markdown(index=False)
        
    except Exception as e:
        return f"获取数据失败: {str(e)}"
```

**5个工具列表：**
1. `get_stock_history` - 获取历史行情（30天，最近10天）
2. `get_stock_news` - 获取最新新闻（最多10条）
3. `get_stock_technical_indicators` - 计算技术指标（MA5/MA10/MA20，涨跌幅）
4. `get_industry_comparison` - 行业对比（市值、市盈率、市净率）
5. `analyze_stock_comprehensive` - 综合分析（一键获取所有信息）

**关键点：**
- ✅ **@tool 装饰器**：函数自动变成 LangChain 工具对象
- ✅ **docstring 文档**：LangChain 自动读取，生成工具描述给 LLM
- ✅ **返回格式**：Markdown 表格，LLM 理解能力最强
- ✅ **错误处理**：工具失败时返回错误信息，不崩溃

---

### 第4页：Agent搭建 - 如何初始化（70秒）⭐⭐⭐

**完整 Agent 初始化代码：**

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import ToolMessage

class StockAnalysisAgent:
    """股票分析 Agent"""
    
    SYSTEM_PROMPT = """你是专业的A股股票分析师。
    
    分析流程：
    1. 理解需求 → 基本面？技术面？新闻面？
    2. 选择工具 → 根据需求调用1-4个工具
    3. 工具调用 → 必须基于真实数据，禁止编造
    4. 输出报告 → 数据呈现 + 专业分析 + 明确建议
    
    重要原则：
    - 所有数据来自工具
    - 工具失败则诚实告知
    - 结合技术+基本面+新闻多维度分析
    """
    
    def __init__(self, model, api_key, base_url):
        # 1️⃣ 初始化 LLM（大语言模型）
        self.llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=0.7  # 温度参数，控制创造性
        )
        
        # 2️⃣ 准备工具（5个股票分析工具）
        self.tools = [
            get_stock_history,
            get_stock_news,
            get_stock_technical_indicators,
            get_industry_comparison,
            analyze_stock_comprehensive
        ]
        self.tool_map = {tool.name: tool for tool in self.tools}
        
        # 3️⃣ 绑定工具到 LLM（核心操作！）
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # 4️⃣ 构建 Prompt（系统提示词 + 消息占位符）
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        # 5️⃣ 创建 Agent Runnable（Prompt + LLM）
        self.agent_runnable = self.prompt | self.llm_with_tools
```

**关键点：**
- ✅ **bind_tools**：让 LLM 知道有哪些工具可用，自动生成工具调用格式
- ✅ **Prompt 工程**：系统提示词引导 AI 按专业步骤思考
- ✅ **Runnable 链**：`prompt | llm_with_tools` 形成可执行的 Agent

---

### 第5页：Agent运行 - 使用Tools和提示词（90秒）⭐⭐⭐

**完整 Agent 运行循环代码：**

```python
def _run_loop(self, input_dict, iteration=0, max_iterations=10):
    """Agent 执行循环（ReAct 模式）"""
    
    # 检查最大迭代次数
    if iteration >= max_iterations:
        return {
            "output": "达到最大迭代次数，无法得出结论",
            "iterations": iteration
        }
    
    # 1️⃣ 调用 LLM（带工具绑定）
    llm_output = self.agent_runnable.invoke(input_dict)
    
    # 2️⃣ 检查是否需要调用工具
    if not llm_output.tool_calls:
        # 没有工具调用，LLM 已经得出结论
        return {
            "output": llm_output.content,
            "iterations": iteration + 1
        }
    
    # 3️⃣ 执行工具调用
    tool_messages = []
    for tool_call in llm_output.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        if tool_name in self.tool_map:
            try:
                # 执行工具，获取真实数据
                tool_output = self.tool_map[tool_name].invoke(tool_args)
                
                # 包装成 ToolMessage（LangChain 消息类型）
                tool_messages.append(
                    ToolMessage(
                        content=str(tool_output),
                        tool_call_id=tool_call["id"]
                    )
                )
            except Exception as e:
                # 工具执行失败，返回错误信息
                tool_messages.append(
                    ToolMessage(
                        content=f"工具执行失败: {str(e)}",
                        tool_call_id=tool_call["id"]
                    )
                )
    
    # 4️⃣ 更新消息历史（LLM输出 + 工具结果）
    messages = input_dict.get("messages", [])
    new_messages = messages + [llm_output] + tool_messages
    
    # 5️⃣ 递归调用（带上工具结果，继续推理）
    return self._run_loop(
        {"messages": new_messages},
        iteration=iteration + 1,
        max_iterations=max_iterations
    )
```

**执行流程示例：**

```
用户查询："分析贵州茅台（600519）的走势"

第1轮：
  LLM 输出：需要调用 get_stock_history("600519")
  → 执行工具 → 获取价格数据表格

第2轮：
  LLM 输入：用户查询 + 价格数据
  LLM 输出：需要调用 get_stock_technical_indicators("600519")
  → 执行工具 → 获取技术指标（MA5/MA10/MA20）

第3轮：
  LLM 输入：用户查询 + 价格数据 + 技术指标
  LLM 输出：综合分析报告（不再调用工具）
  → 返回最终结果
```

**关键点：**
- ✅ **ReAct 模式**：Reasoning（推理） → Action（行动） → Observation（观察）
- ✅ **递归实现**：每轮逻辑完全一致，代码简洁优雅
- ✅ **消息历史**：LLM 能看到所有历史对话和工具结果
- ✅ **自主决策**：AI 自己决定调用哪些工具、调用几次、何时停止

---

### 第6页：前端展示 - Streamlit UI（40秒）

**核心前端代码：**

```python
import streamlit as st
from src.agent import StockAnalysisAgent

# 页面配置
st.set_page_config(page_title="AI Stock Analysis", layout="wide")

# 侧边栏：API 配置
with st.sidebar:
    api_key = st.text_input("API 密钥", type="password")
    base_url = st.text_input("API 地址", value="https://api.siliconflow.cn/v1")
    model = st.text_input("模型", value="Qwen/Qwen2.5-7B-Instruct")

# 主界面：查询输入
user_input = st.text_area("输入您的问题", height=100)

if st.button("🚀 开始分析"):
    # 初始化 Agent
    agent = StockAnalysisAgent(model=model, api_key=api_key, base_url=base_url)
    
    # 执行查询
    with st.spinner("AI 正在分析中..."):
        result = agent.run(user_input)
    
    # 显示结果
    st.success(result["output"])
    st.caption(f"用了 {result['iterations']} 步完成分析")
```

**UI 特点：**
- ✅ **简洁美观**：现代化设计，响应式布局
- ✅ **API 配置**：用户可自行输入 API 密钥
- ✅ **实时反馈**：显示分析进度和步骤数
- ✅ **历史记录**：保存查询历史，方便回顾

**部署方式：**
- Streamlit Cloud 一键部署
- 获得永久访问链接
- 支持公开分享

---

### 第7页：总结（20秒）

**核心创新点：**
1. ✅ **自主决策** - Agent 自动选择调用哪些工具
2. ✅ **多轮推理** - 支持复杂查询的分步分析
3. ✅ **专业输出** - 系统提示词引导专业分析
4. ✅ **易于部署** - Streamlit Cloud 一键部署

**技术栈：**
- LangChain（Agent 框架）
- AkShare（数据源）
- Streamlit（Web UI）

**代码量：** ~700 行  
**功能：** 5 个专业分析工具 + 完整 Agent + Web UI

---

**汇报完毕，谢谢！**

---

## 时间分配（总计：350秒 = 5分50秒）

| 页数 | 内容 | 时间 | 累计 |
|------|------|------|------|
| 1 | 标题页 | 10s | 10s |
| 2 | 系统架构（整体流程） | 40s | 50s |
| 3 | 工具实现（详细代码） | 80s | 130s |
| 4 | Agent搭建（详细代码） | 70s | 200s |
| 5 | Agent运行（详细代码） | 90s | 290s |
| 6 | 前端展示 | 40s | 330s |
| 7 | 总结 | 20s | 350s |

**目标时长：** 5分50秒（如果时间不够，可以压缩到4分30秒）

**压缩建议（如果时间紧张）：**
- 工具实现：80s → 60s（只讲一个完整例子）
- Agent搭建：70s → 60s（简化代码展示）
- Agent运行：90s → 70s（简化流程示例）
- 前端展示：40s → 30s（快速带过）

**压缩后总时长：** 约4分30秒
