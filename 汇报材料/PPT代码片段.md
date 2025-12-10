# PPT 代码片段 - 复制粘贴版（逻辑顺序版）

> 这些代码片段已经详细格式化，可以直接复制到 PPT 中  
> 建议使用代码高亮工具（如 Carbon、Ray.so）生成漂亮的代码截图  
> **注意：** 代码已增加细节，便于详细讲解

---

## 代码片段1：工具实现 - 完整示例

**用于：** 第3页 PPT  
**文件：** `src/tools/stock_data.py`

```python
from langchain_core.tools import tool
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

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
            start_date=start_date, # 开始日期（30天前）
            end_date=end_date,     # 结束日期（今天）
            adjust="qfq"           # 前复权（分析价格趋势通常用前复权）
        )
        
        if df.empty:
            return "未找到该股票数据，请确认代码是否正确。"
        
        # 2. 数据清洗（只保留关键字段和最近10天）
        df = df[['日期', '开盘', '收盘', '最高', '最低', '成交量']]
        recent_data = df.tail(10).copy()
        
        # 插入 id 列作为第一列
        recent_data.insert(0, 'id', range(1, len(recent_data) + 1))
        
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

**讲解要点：**
- ✅ @tool 装饰器：函数 → 工具对象（自动）
- ✅ docstring 是工具描述，AI 通过它理解工具功能
- ✅ 返回 Markdown 格式，LLM 理解能力最强
- ✅ 错误处理：工具失败时返回错误信息，不崩溃

---

## 代码片段2：Agent 搭建 - 完整初始化

**用于：** 第4页 PPT  
**文件：** `src/agent/stock_agent.py`

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
        # 创建工具映射字典，方便快速查找
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

**讲解要点：**
- ✅ bind_tools 是关键：让 LLM 知道有哪些工具可用，自动生成工具调用格式
- ✅ 5个工具覆盖股票分析所需的所有数据
- ✅ Prompt 工程引导 AI 专业分析
- ✅ Runnable 链：`prompt | llm_with_tools` 形成可执行的 Agent

---

## 代码片段3：Agent 运行 - 完整循环

**用于：** 第5页 PPT  
**文件：** `src/agent/stock_agent.py`

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
                        tool_call_id=tool_call["id"]  # 关联工具调用ID
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

**讲解要点：**
- ✅ ReAct = Reasoning（推理） → Action（行动） → Observation（观察）
- ✅ 递归实现，每轮调用逻辑完全一致
- ✅ 消息历史：LLM 能看到所有历史对话和工具结果
- ✅ AI 自主决定调用哪些工具、调用几次

---

## 代码片段4：前端展示 - Streamlit UI

**用于：** 第6页 PPT  
**文件：** `ui/streamlit_app_with_login.py`

```python
import streamlit as st
from src.agent import StockAnalysisAgent

# 页面配置
st.set_page_config(
    page_title="AI Stock Analysis",
    page_icon="📊",
    layout="wide"
)

# 侧边栏：API 配置
with st.sidebar:
    st.title("⚙️ API 配置")
    
    api_key = st.text_input(
        "API 密钥",
        type="password",
        placeholder="sk-xxx 或你的 API 密钥"
    )
    
    base_url = st.text_input(
        "API 地址",
        value="https://api.siliconflow.cn/v1",
        placeholder="https://api.siliconflow.cn/v1"
    )
    
    model = st.text_input(
        "模型",
        value="Qwen/Qwen2.5-7B-Instruct",
        placeholder="Qwen/Qwen2.5-7B-Instruct"
    )

# 主界面：查询输入
st.title("📊 AI 股票分析助手")

user_input = st.text_area(
    "输入您的问题",
    height=100,
    placeholder="例如：分析贵州茅台（600519）的走势"
)

if st.button("🚀 开始分析"):
    # 初始化 Agent
    agent = StockAnalysisAgent(
        model=model,
        api_key=api_key,
        base_url=base_url
    )
    
    # 执行查询
    with st.spinner("🤔 AI 正在分析中..."):
        result = agent.run(user_input)
    
    # 显示结果
    st.success(result["output"])
    st.caption(f"✅ 用了 {result['iterations']} 步完成分析")
```

**讲解要点：**
- ✅ 简洁美观：现代化设计，响应式布局
- ✅ API 配置：用户可自行输入 API 密钥
- ✅ 实时反馈：显示分析进度和步骤数
- ✅ 部署方式：Streamlit Cloud 一键部署

---

## 其他辅助代码片段

### AkShare API 调用示例

```python
import akshare as ak

# 获取股票历史数据
df = ak.stock_zh_a_hist(
    symbol="600519",    # 贵州茅台
    period="daily",     # 日线
    start_date="20240101",
    end_date="20240201",
    adjust="qfq"        # 前复权
)

# 获取股票新闻
news_df = ak.stock_news_em(symbol="600519")

# 获取股票基本信息
info_df = ak.stock_individual_info_em(symbol="600519")
```

---

### LangChain 工具绑定示例

```python
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

# 定义工具
@tool
def calculator(a: int, b: int) -> int:
    """计算两个数的和"""
    return a + b

# 初始化 LLM
llm = ChatOpenAI(model="gpt-4")

# 绑定工具
llm_with_tools = llm.bind_tools([calculator])

# 调用
response = llm_with_tools.invoke("1 + 2 等于多少？")
# → LLM 会自动调用 calculator(1, 2)
```

---

## 💡 代码截图建议

### 推荐工具

1. **Carbon** (https://carbon.now.sh)
   - 优点：漂亮的渐变背景，支持多种主题
   - 适合：展示完整代码块

2. **Ray.so** (https://ray.so)
   - 优点：简洁风格，Mac 窗口样式
   - 适合：展示关键代码片段

3. **PowerPoint 原生代码块**
   - 优点：可编辑，大小自由
   - 缺点：需要手动设置字体和颜色

### 代码高亮配置

**推荐主题：**
- Monokai（深色，对比强）
- GitHub Light（浅色，清晰）
- Dracula（紫色系，现代感）

**字体建议：**
- Fira Code（带连字，美观）
- Consolas（Windows 默认，清晰）
- Monaco（Mac 默认，专业）

**字号建议：**
- PPT 屏幕：16-18pt
- 投影仪：18-20pt（更大更清晰）

---

## ✅ 使用清单

### 准备 PPT 时

- [ ] 复制对应代码片段到 PPT
- [ ] 使用代码截图工具生成漂亮截图
- [ ] 关键行用红色/黄色高亮标注
- [ ] 添加注释箭头指向关键代码
- [ ] 测试投影效果（文字是否清晰）
- [ ] **确保代码完整，便于详细讲解**

### 讲解代码时

- [ ] 先读代码（1-2秒静默）
- [ ] 逐行解释（用通俗语言）
- [ ] 强调关键词（@tool、bind_tools、递归）
- [ ] 用手势指向代码（激光笔或鼠标）
- [ ] 讲完后停顿2秒（让观众消化）

---

**祝汇报成功！🎉**
