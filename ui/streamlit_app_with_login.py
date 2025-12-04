# -*- coding: utf-8 -*-
"""
Stock Analysis Agent - With API Configuration
支持用户自行配置 API，可公开部署
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 安全的编码设置
try:
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
except:
    pass

os.environ['PYTHONIOENCODING'] = 'utf-8'

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import ToolMessage
from dotenv import load_dotenv

from src.tools import (
    get_stock_history,
    get_stock_news,
    get_stock_technical_indicators,
    get_industry_comparison,
    analyze_stock_comprehensive
)

# 页面配置
st.set_page_config(
    page_title="AI Stock Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS - 简洁版本
st.markdown("""
<style>
    /* 主背景 */
    .main {background: #fafafa;}
    
    /* 侧边栏加宽 */
    [data-testid="stSidebar"] {
        min-width: 380px !important;
        max-width: 380px !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        width: 380px !important;
    }
    
    /* 按钮样式 */
    .stButton>button {
        background: #1a1a1a;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        border: none;
        font-weight: 500;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background: #404040;
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

load_dotenv()

# ==================== 侧边栏：API 配置 ====================
st.sidebar.title("⚙️ API 配置")
st.sidebar.markdown("---")

# 初始化 session state
if 'api_configured' not in st.session_state:
    st.session_state.api_configured = False
if 'history' not in st.session_state:
    st.session_state.history = []
if 'current_input' not in st.session_state:
    st.session_state.current_input = ""

# 检查是否有 Streamlit Secrets
has_secrets = False
try:
    if hasattr(st, 'secrets') and 'api-key' in st.secrets:
        has_secrets = True
        st.sidebar.success("✅ 使用 Streamlit Secrets 配置")
        st.session_state.api_configured = True
        api_key = st.secrets['api-key']
        base_url = st.secrets.get('base-url', 'https://api.siliconflow.cn/v1')
        model = st.secrets.get('model', 'Qwen/Qwen2.5-7B-Instruct')
except:
    pass

# 如果没有 Secrets，让用户输入
if not has_secrets:
    st.sidebar.markdown("### 🔑 输入 API 密钥")
    st.sidebar.info("💡 API 密钥仅保存在当前会话中（不会持久化）")
    
    with st.sidebar.form("api_config_form"):
        api_key_input = st.text_input(
            "API 密钥",
            type="password",
            placeholder="sk-xxx 或你的 API 密钥",
            help="从 SiliconFlow、智谱 AI 等平台获取免费 API"
        )
        
        base_url_input = st.text_input(
            "API 地址",
            value="https://api.siliconflow.cn/v1",
            placeholder="https://api.siliconflow.cn/v1"
        )
        
        model_input = st.text_input(
            "模型",
            value="Qwen/Qwen2.5-7B-Instruct",
            placeholder="Qwen/Qwen2.5-7B-Instruct"
        )
        
        test_btn = st.form_submit_button("🧪 测试并保存", use_container_width=True)
        
        if test_btn and api_key_input:
            # 测试 API
            try:
                test_llm = ChatOpenAI(
                    model=model_input,
                    api_key=api_key_input,
                    base_url=base_url_input,
                    temperature=0.3,
                    timeout=10
                )
                # 简单测试
                test_llm.invoke("Hi")
                
                # 保存到 session
                st.session_state.api_key = api_key_input
                st.session_state.base_url = base_url_input
                st.session_state.model = model_input
                st.session_state.api_configured = True
                
                st.sidebar.success("✅ API 可用！可以开始分析了")
                st.rerun()
                
            except Exception as e:
                st.sidebar.error(f"❌ API 测试失败: {type(e).__name__}")
                st.sidebar.info("💡 请检查 API 密钥和地址是否正确")
        
        elif test_btn and not api_key_input:
            st.sidebar.warning("⚠️ 请输入 API 密钥")
    
    # 获取免费 API 链接
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🆓 获取免费 API")
    st.sidebar.markdown("""
    **推荐平台：**
    - [SiliconFlow](https://siliconflow.cn) - 免费额度充足
    - [智谱 AI](https://open.bigmodel.cn) - 新用户免费 tokens
    - [月之暗面](https://platform.moonshot.cn) - 新用户礼包
    """)
    
    # 使用步骤
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📖 使用步骤")
    st.sidebar.markdown("""
    **第一步：获取 API**
    1. 点击上方任一平台链接
    2. 注册账号（手机号即可）
    3. 进入控制台创建 API 密钥
    4. 复制 API 密钥
    
    **第二步：配置**
    1. 将 API 密钥粘贴到上方输入框
    2. 确认 API 地址正确
    3. 点击"测试并保存"
    4. 看到✅表示成功
    
    **第三步：使用**
    1. 在右侧点击示例按钮
    2. 或输入你的问题
    3. 点击"开始分析"
    4. 等待 AI 分析结果
    
    **提示：**
    - API 密钥仅本次会话有效
    - 刷新页面需重新输入
    - 分析需要 10-30 秒
    """)
    
    # 从 session 读取（如果已配置）
    if st.session_state.api_configured:
        api_key = st.session_state.api_key
        base_url = st.session_state.base_url
        model = st.session_state.model
        st.sidebar.success("✅ API 已配置")
        if st.sidebar.button("🔄 重新配置", use_container_width=True):
            st.session_state.api_configured = False
            st.rerun()

# ==================== 主界面 ====================

# 检查 API 是否配置
if not st.session_state.api_configured:
    st.title("📊 AI 股票分析助手")
    st.markdown("---")
    st.info("👈 请在左侧边栏配置 API 后开始使用")
    
    st.markdown("### 🚀 快速开始")
    st.markdown("""
    1. 从 [SiliconFlow](https://siliconflow.cn) 或其他平台获取免费 API 密钥
    2. 在左侧边栏输入 API 密钥
    3. 点击"测试并保存"
    4. 开始分析股票！
    """)
    
    st.markdown("### 💡 功能特色")
    col1, col2, col3 = st.columns(3)
    col1.markdown("📈 **历史走势**\n分析价格趋势")
    col2.markdown("📰 **最新新闻**\n获取市场动态")
    col3.markdown("📊 **技术指标**\nMACD、RSI、均线等")
    
    st.stop()

# API 已配置，显示主界面
st.title("📊 AI 股票分析助手")
st.caption("基于 LangChain 和 AkShare · 支持中英文查询")
st.markdown("---")

# 快速示例
st.subheader("💡 快速示例")

examples = [
    "分析贵州茅台（600519）的走势",
    "获取平安银行（000001）的最新新闻",
    "计算招商银行（600036）的技术指标",
    "对比五粮液（000858）的行业地位",
    "综合分析宁德时代（300750）"
]

cols = st.columns(5)
for idx, (col, example) in enumerate(zip(cols, examples)):
    with col:
        if st.button(f"示例 {idx+1}", key=f"ex_{idx}", use_container_width=True):
            st.session_state.current_input = example
            st.rerun()

# 输入区域
st.markdown("### 🔍 输入您的问题")

user_input = st.text_area(
    "",
    value=st.session_state.current_input,
    height=100,
    placeholder="例如：分析贵州茅台的技术指标和最新新闻",
    label_visibility="collapsed"
)

if user_input != st.session_state.current_input:
    st.session_state.current_input = user_input

# 按钮
col1, col2 = st.columns([1, 5])
with col1:
    analyze_btn = st.button("🚀 开始分析", type="primary", use_container_width=True)
    clear_btn = st.button("🗑️ 清空历史", use_container_width=True)

if clear_btn:
    st.session_state.history = []
    st.session_state.current_input = ""
    st.success("✅ 已清空历史记录！")
    st.rerun()

# 执行分析
if analyze_btn and user_input:
    progress_container = st.empty()
    
    with progress_container:
        with st.spinner("🤔 AI 正在分析中..."):
            try:
                tools = [
                    get_stock_history,
                    get_stock_news,
                    get_stock_technical_indicators,
                    get_industry_comparison,
                    analyze_stock_comprehensive
                ]
                tool_map = {tool.name: tool for tool in tools}
                
                llm = ChatOpenAI(
                    model=model,
                    api_key=api_key,
                    base_url=base_url,
                    temperature=0.7
                )
                
                llm_with_tools = llm.bind_tools(tools)
                
                system_prompt = """你是一位拥有10年以上经验的资深股票分析师。

重要：你的职责是进行深度分析，而不是简单展示数据。

回答问题时：
1. 使用工具获取真实数据
2. 深度分析数据：
   - 这些数字说明了什么？
   - 趋势是什么？
   - 风险和机会在哪里？
3. 提供专业洞察：
   - 技术分析（支撑/阻力位、趋势、信号）
   - 基本面分析（估值、增长、竞争地位）
   - 市场情绪（新闻解读、行业展望）
4. 给出明确结论：
   - 综合评估（看涨/看跌/中性）
   - 投资者关键要点
   - 风险提示

不要只是罗列数据，要解读数据并给出专业意见。

支持中英文查询，根据用户提问语言回复。"""

                prompt = ChatPromptTemplate.from_messages([
                    ("system", system_prompt),
                    MessagesPlaceholder(variable_name="messages"),
                ])
                
                messages = [{"role": "user", "content": user_input}]
                iteration_count = 0
                
                for i in range(10):
                    iteration_count = i + 1
                    response = (prompt | llm_with_tools).invoke({"messages": messages})
                    
                    if not response.tool_calls:
                        st.session_state.history.insert(0, {
                            "query": user_input,
                            "result": response.content,
                            "time": datetime.now().strftime("%H:%M"),
                            "steps": iteration_count
                        })
                        st.session_state.current_input = ""
                        progress_container.empty()
                        st.success(f"✅ 分析完成！（用了 {iteration_count} 步）")
                        st.rerun()
                        break
                    
                    messages.append(response)
                    
                    for tool_call in response.tool_calls:
                        tool_name = tool_call["name"]
                        tool_args = tool_call["args"]
                        
                        if tool_name in tool_map:
                            try:
                                output = tool_map[tool_name].invoke(tool_args)
                                messages.append(ToolMessage(
                                    content=str(output),
                                    tool_call_id=tool_call["id"]
                                ))
                            except Exception as e:
                                messages.append(ToolMessage(
                                    content=f"Error: {type(e).__name__}",
                                    tool_call_id=tool_call["id"]
                                ))
                else:
                    progress_container.empty()
                    st.warning("⚠️ 达到最大迭代次数")
                
            except Exception as e:
                progress_container.empty()
                st.error(f"❌ 错误: {type(e).__name__}")
                st.info("💡 请检查左侧边栏的 API 配置")

# 显示结果
if st.session_state.history:
    st.markdown("---")
    st.subheader("📊 分析结果")
    
    col1, col2, col3 = st.columns(3)
    latest = st.session_state.history[0]
    
    col1.metric("分析步骤", latest.get('steps', '?'))
    col2.metric("结果长度", len(latest['result']))
    col3.metric("历史记录", len(st.session_state.history))
    
    st.markdown("#### 🔍 查询")
    st.info(latest['query'])
    
    st.markdown("#### ✨ 分析结果")
    st.success(latest['result'])
    
    st.caption(f"⏱️ {latest['time']} · 🔄 {latest.get('steps', '?')} 步")
    
    if len(st.session_state.history) > 1:
        st.markdown("---")
        st.markdown("### 📜 历史记录")
        
        for record in st.session_state.history[1:6]:
            with st.expander(f"{record['time']} - {record['query'][:40]}..."):
                st.markdown(f"**查询：** {record['query']}")
                st.caption(f"步骤: {record.get('steps', '?')}")
                st.divider()
                st.write(record['result'])

else:
    st.info("👆 点击上方示例按钮，或输入您的问题")

st.markdown("---")
st.caption("基于 LangChain × AkShare 构建 · ⚠️ 仅供学习使用，不构成投资建议")
