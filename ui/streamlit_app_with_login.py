# -*- coding: utf-8 -*-
"""
Stock Analysis Agent - Modern UI
现代化深色主题 UI，基于 Glassmorphism 和渐变设计
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

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="AI Stock Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 现代化 CSS 样式 ====================
st.markdown("""
<style>
    /* ===== 导入字体 ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* ===== 全局样式 ===== */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* ===== 深色背景 ===== */
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* ===== 侧边栏 ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1a 100%);
        border-right: 1px solid rgba(102, 126, 234, 0.2);
        min-width: 350px !important;
        max-width: 350px !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent;
        padding: 1.5rem;
    }
    
    /* ===== 增强版毛玻璃效果 ===== */
    .glass-card {
        background: linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.1) 0%,
            rgba(255, 255, 255, 0.05) 50%,
            rgba(255, 255, 255, 0.02) 100%
        );
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 
            0 4px 30px rgba(0, 0, 0, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    
    /* 玻璃高光效果 */
    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.1),
            transparent
        );
        transition: left 0.5s ease;
    }
    
    .glass-card:hover::before {
        left: 100%;
    }
    
    .glass-card:hover {
        background: linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.15) 0%,
            rgba(255, 255, 255, 0.08) 50%,
            rgba(255, 255, 255, 0.05) 100%
        );
        border-color: rgba(102, 126, 234, 0.4);
        transform: translateY(-4px) scale(1.01);
        box-shadow: 
            0 20px 40px rgba(102, 126, 234, 0.2),
            0 0 0 1px rgba(102, 126, 234, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
    }
    
    /* 玻璃边框发光 */
    .glass-card::after {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(
            45deg,
            transparent 30%,
            rgba(102, 126, 234, 0.3) 50%,
            transparent 70%
        );
        border-radius: 22px;
        z-index: -1;
        opacity: 0;
        transition: opacity 0.4s ease;
    }
    
    .glass-card:hover::after {
        opacity: 1;
    }
    
    /* ===== 英雄区域 ===== */
    .hero-section {
        text-align: center;
        padding: 2rem 0 3rem 0;
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .hero-subtitle {
        color: rgba(255, 255, 255, 0.6);
        font-size: 1.1rem;
        font-weight: 400;
    }
    
    /* ===== 输入框 ===== */
    .stTextArea textarea, .stTextInput input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
    }
    
    .stTextArea textarea::placeholder, .stTextInput input::placeholder {
        color: rgba(255, 255, 255, 0.4) !important;
    }
    
    /* ===== 按钮 ===== */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* 次要按钮 */
    .secondary-btn button {
        background: rgba(255, 255, 255, 0.1) !important;
        box-shadow: none !important;
    }
    
    .secondary-btn button:hover {
        background: rgba(255, 255, 255, 0.15) !important;
        box-shadow: none !important;
    }
    
    /* ===== 示例按钮 - 增强玻璃效果 ===== */
    .example-btn button {
        background: linear-gradient(
            135deg,
            rgba(102, 126, 234, 0.2) 0%,
            rgba(118, 75, 162, 0.15) 100%
        ) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(102, 126, 234, 0.3) !important;
        border-radius: 12px !important;
        box-shadow: 
            0 4px 15px rgba(102, 126, 234, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        padding: 0.6rem 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .example-btn button:hover {
        background: linear-gradient(
            135deg,
            rgba(102, 126, 234, 0.35) 0%,
            rgba(118, 75, 162, 0.25) 100%
        ) !important;
        border-color: rgba(102, 126, 234, 0.6) !important;
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 
            0 8px 25px rgba(102, 126, 234, 0.3),
            0 0 20px rgba(102, 126, 234, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
    }
    
    .example-btn button:active {
        transform: translateY(0) scale(0.98) !important;
    }
    
    /* ===== 指标卡片 ===== */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        text-align: center;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-label {
        color: rgba(255, 255, 255, 0.5);
        font-size: 0.85rem;
        margin-top: 0.25rem;
    }
    
    /* ===== 结果展示 ===== */
    .result-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        position: relative;
        overflow: hidden;
    }
    
    .result-card::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .result-card .content {
        padding-left: 1rem;
    }
    
    /* ===== 查询标签 ===== */
    .query-tag {
        display: inline-block;
        background: rgba(102, 126, 234, 0.2);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 8px;
        padding: 0.5rem 1rem;
        color: #a0aeff;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    
    /* ===== 标题样式 ===== */
    h1, h2, h3 {
        color: #ffffff !important;
    }
    
    .section-title {
        color: #ffffff;
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* ===== 信息提示 ===== */
    .stInfo, .stSuccess, .stWarning, .stError {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
    }
    
    /* ===== Expander ===== */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #ffffff !important;
    }
    
    .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
    }
    
    /* ===== 分隔线 ===== */
    hr {
        border-color: rgba(255, 255, 255, 0.1) !important;
        margin: 2rem 0 !important;
    }
    
    /* ===== 标签文字 ===== */
    .stMarkdown p, .stMarkdown li {
        color: rgba(255, 255, 255, 0.8);
    }
    
    label {
        color: rgba(255, 255, 255, 0.7) !important;
    }
    
    /* ===== 链接 ===== */
    a {
        color: #667eea !important;
        text-decoration: none !important;
        transition: color 0.2s ease !important;
    }
    
    a:hover {
        color: #a0aeff !important;
    }
    
    /* ===== 滚动条 ===== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(102, 126, 234, 0.3);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(102, 126, 234, 0.5);
    }
    
    /* ===== Spinner ===== */
    .stSpinner > div {
        border-color: #667eea !important;
    }
    
    /* ===== Footer ===== */
    .footer {
        text-align: center;
        color: rgba(255, 255, 255, 0.4);
        font-size: 0.85rem;
        padding: 2rem 0;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        margin-top: 3rem;
    }
    
    /* ===== 动画 ===== */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-in {
        animation: fadeIn 0.5s ease forwards;
    }
    
    /* ===== 表单 ===== */
    [data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

load_dotenv()

# ==================== 初始化 Session State ====================
if 'api_configured' not in st.session_state:
    st.session_state.api_configured = False
if 'history' not in st.session_state:
    st.session_state.history = []
if 'current_input' not in st.session_state:
    st.session_state.current_input = ""
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'base_url' not in st.session_state:
    st.session_state.base_url = "https://api.siliconflow.cn/v1"
if 'model' not in st.session_state:
    st.session_state.model = "Qwen/Qwen2.5-7B-Instruct"

# 定义全局 API 变量（从 session state 读取）
api_key = st.session_state.api_key
base_url = st.session_state.base_url
model = st.session_state.model

# ==================== 侧边栏 ====================
with st.sidebar:
    # Logo 和标题
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 2rem 0;">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;"></div>
        <div style="font-size: 2.25rem; font-weight: 600; color: #ffffff;">AI Stock Agent</div>
        <div style="font-size: 1.85rem; color: rgba(255,255,255,0.5);">智能股票分析助手</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 检查 Streamlit Secrets
    has_secrets = False
    try:
        if hasattr(st, 'secrets') and 'api-key' in st.secrets:
            has_secrets = True
            st.success("✅ 已使用 Secrets 配置")
            st.session_state.api_configured = True
            st.session_state.api_key = st.secrets['api-key']
            st.session_state.base_url = st.secrets.get('base-url', 'https://api.siliconflow.cn/v1')
            st.session_state.model = st.secrets.get('model', 'Qwen/Qwen2.5-7B-Instruct')
    except:
        pass
    
    # API 配置表单
    if not has_secrets:
        st.markdown("### 🔑 API 配置")
        
        # 先检查是否已配置
        if st.session_state.api_configured:
            st.success(f"✅ API 已配置 (模型: {st.session_state.model})")
            
            if st.button("🔄 重新配置", use_container_width=True):
                st.session_state.api_configured = False
                st.rerun()
        else:
            # 未配置时显示表单
            with st.form("api_config_form"):
                api_key_input = st.text_input(
                    "API 密钥",
                    type="password",
                    placeholder="sk-xxx",
                    help="从 SiliconFlow 等平台获取"
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
                
                test_btn = st.form_submit_button("🧪 测试连接", use_container_width=True)
                
                if test_btn and api_key_input:
                    try:
                        test_llm = ChatOpenAI(
                            model=model_input,
                            api_key=api_key_input,
                            base_url=base_url_input,
                            temperature=0.3,
                            timeout=10
                        )
                        test_llm.invoke("Hi")
                        
                        st.session_state.api_key = api_key_input
                        st.session_state.base_url = base_url_input
                        st.session_state.model = model_input
                        st.session_state.api_configured = True
                        
                        st.success("✅ 连接成功！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 连接失败: {str(e)}")
                elif test_btn:
                    st.warning("⚠️ 请输入 API 密钥")
        
        st.markdown("---")
        
        # 获取 API 链接
        st.markdown("### 🆓 免费 API")
        st.markdown("""
        - [SiliconFlow](https://siliconflow.cn) - 推荐 ⭐
        - [智谱 AI](https://open.bigmodel.cn)
        - [月之暗面](https://platform.moonshot.cn)
        """)
    
    st.markdown("---")
    
    # 快速示例
    st.markdown("### 💡 快速示例")
    
    examples = [
        ("📈 茅台走势", "分析贵州茅台（600519）的走势"),
        ("📰 平安新闻", "获取平安银行（000001）的最新新闻"),
        ("📊 招行指标", "计算招商银行（600036）的技术指标"),
        ("🏭 五粮液对比", "对比五粮液（000858）的行业地位"),
        ("🔍 宁德综合", "综合分析宁德时代（300750）")
    ]
    
    st.markdown('<div class="example-btn">', unsafe_allow_html=True)
    for label, query in examples:
        if st.button(label, key=f"ex_{label}", use_container_width=True):
            st.session_state.user_input_area = query
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== 主界面 ====================

# 英雄区域
st.markdown("""
<div class="hero-section">
    <h1 class="hero-title">AI Stock Analysis</h1>
    <p class="hero-subtitle">基于 LangChain 和 AkShare 的智能 A 股分析系统</p>
</div>
""", unsafe_allow_html=True)

# 检查 API 配置
if not st.session_state.api_configured:
    st.markdown("""
    <div class="glass-card" style="text-align: center; padding: 3rem;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🔐</div>
        <div style="color: #ffffff; font-size: 1.25rem; margin-bottom: 0.5rem;">请先配置 API</div>
        <div style="color: rgba(255,255,255,0.5);">在左侧边栏输入您的 API 密钥以开始使用</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 功能介绍
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="glass-card" style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📈</div>
            <div style="color: #ffffff; font-weight: 600;">历史走势</div>
            <div style="color: rgba(255,255,255,0.5); font-size: 0.85rem;">获取股票价格和成交量数据</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="glass-card" style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
            <div style="color: #ffffff; font-weight: 600;">技术分析</div>
            <div style="color: rgba(255,255,255,0.5); font-size: 0.85rem;">计算 MACD、RSI、均线等指标</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="glass-card" style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📰</div>
            <div style="color: #ffffff; font-weight: 600;">新闻资讯</div>
            <div style="color: rgba(255,255,255,0.5); font-size: 0.85rem;">获取最新市场动态和新闻</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.stop()

# ==================== 已配置 API，显示主功能 ====================

# 输入区域
st.markdown('<div class="section-title">🔍 输入您的分析需求</div>', unsafe_allow_html=True)

# 使用 key 直接绑定到 session_state
if 'user_input_area' not in st.session_state:
    st.session_state.user_input_area = st.session_state.current_input

user_input = st.text_area(
    "分析需求",
    height=120,
    placeholder="例如：分析贵州茅台（600519）的技术指标和最新新闻，给出投资建议...",
    label_visibility="collapsed",
    key="user_input_area"
)

# 按钮行
col1, col2, col3 = st.columns([1, 1, 3])

with col1:
    analyze_btn = st.button("🚀 开始分析", type="primary", use_container_width=True)

with col2:
    clear_btn = st.button("🗑️ 清空", use_container_width=True)

if clear_btn:
    st.session_state.history = []
    st.session_state.current_input = ""
    st.success("✅ 已清空！")
    st.rerun()

# ==================== 执行分析 ====================
if analyze_btn and user_input:
    progress_container = st.empty()
    
    with progress_container:
        with st.spinner("🤔 AI 正在深度分析中，请稍候..."):
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
                    model=st.session_state.model,
                    api_key=st.session_state.api_key,
                    base_url=st.session_state.base_url,
                    temperature=0.7
                )
                
                llm_with_tools = llm.bind_tools(tools)
                
                system_prompt = """你是一位拥有10年以上经验的资深股票分析师。

⚠️ 重要规则：
1. **必须使用工具获取真实数据** - 如果工具调用失败，明确告知用户
2. **不要编造数据** - 没有数据就说没有，不要说"无法获取但我们可以推断"
3. **数据来源说明** - 本系统使用 AkShare，主要支持中国 A 股数据

数据范围：
- ✅ 支持：沪深 A 股（如 600519 贵州茅台、000001 平安银行）
- ❌ 不支持：美股、港股、其他国际市场

分析流程：
1. 使用工具获取真实数据
2. 深度分析：趋势、风险、机会
3. 专业洞察：技术面、基本面、市场情绪
4. 明确结论：评估、要点、风险提示

记住：诚实 > 空谈。没有数据就说没有！"""

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
                    st.warning("⚠️ 达到最大分析轮次")
                
            except Exception as e:
                progress_container.empty()
                st.error(f"❌ 分析出错: {type(e).__name__}")

# ==================== 显示分析结果 ====================
if st.session_state.history:
    st.markdown("---")
    
    latest = st.session_state.history[0]
    
    # 指标卡片
    st.markdown('<div class="section-title">📊 分析概览</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = [
        ("分析步骤", latest.get('steps', '?'), "🔄"),
        ("结果长度", len(latest['result']), "📝"),
        ("历史记录", len(st.session_state.history), "📚"),
        ("完成时间", latest['time'], "⏱️")
    ]
    
    for col, (label, value, icon) in zip([col1, col2, col3, col4], metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.5rem; margin-bottom: 0.25rem;">{icon}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 查询内容
    st.markdown('<div class="section-title">🔍 分析查询</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="query-tag">{latest['query']}</div>
    """, unsafe_allow_html=True)
    
    # 分析结果
    st.markdown('<div class="section-title">✨ 分析结果</div>', unsafe_allow_html=True)
    
    # 直接渲染 Markdown 结果
    st.markdown(latest['result'])
    
    # 历史记录
    if len(st.session_state.history) > 1:
        st.markdown("---")
        st.markdown('<div class="section-title">📜 历史记录</div>', unsafe_allow_html=True)
        
        for idx, record in enumerate(st.session_state.history[1:6]):
            with st.expander(f"⏱️ {record['time']} - {record['query'][:50]}..."):
                st.markdown(f"**查询：** {record['query']}")
                st.caption(f"分析步骤: {record.get('steps', '?')}")
                st.divider()
                st.write(record['result'])

else:
    # 没有历史记录时的提示
    st.markdown("""
    <div class="glass-card" style="text-align: center; padding: 3rem; margin-top: 2rem;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">💡</div>
        <div style="color: #ffffff; font-size: 1.1rem; margin-bottom: 0.5rem;">准备好开始了吗？</div>
        <div style="color: rgba(255,255,255,0.5);">在上方输入您的分析需求，或点击左侧示例快速开始</div>
    </div>
    """, unsafe_allow_html=True)

# ==================== 页脚 ====================
st.markdown("""
<div class="footer">
    <div>基于 LangChain × AkShare 构建</div>
    <div style="margin-top: 0.5rem;">⚠️ 仅供学习研究使用，不构成任何投资建议</div>
</div>
""", unsafe_allow_html=True)
