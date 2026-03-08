"""
Stock Analysis Tools Module
股票分析工具模块
"""

# ── 全局请求超时保护 ─────────────────────────────────────────────────
# akshare 底层使用 requests，对某些网络环境下的接口会无限等待。
# 在所有 akshare 调用开始之前注入全局超时（8s）和禁止代理，防止挂起。
import requests as _requests

_orig_request = _requests.Session.request

def _patched_request(self, method, url, **kwargs):
    kwargs.setdefault('timeout', 8)   # 最多等待 8 秒
    self.trust_env = False            # 不读取系统代理，避免 VPN 跳转失败卡死
    return _orig_request(self, method, url, **kwargs)

_requests.Session.request = _patched_request
# ────────────────────────────────────────────────────────────────────


from .stock_data import (
    get_stock_history,
    get_stock_news,
    get_stock_technical_indicators,
    get_industry_comparison,
    analyze_stock_comprehensive,
    get_northbound_flow,
    get_dragon_tiger_board,
)

from .news_analysis_tools import (
    analyze_news_sentiment,
    get_macroeconomic_indicators,
    assess_event_impact,
    get_global_market_news
)

from .sentiment_tools import (
    analyze_social_media_sentiment,
    get_public_sentiment_score,
    track_market_mood
)

from .fundamentals_tools import (
    get_company_financials,
    calculate_intrinsic_value,
    get_performance_metrics,
    identify_red_flags
)

from .tool_registry import (
    ToolRegistry,
    tool_registry,
    init_tool_registry,
    get_tool_registry,
)

from .risk_metrics import (
    calculate_volatility,
    calculate_beta,
    calculate_max_drawdown,
    calculate_sharpe_ratio,
    calculate_var,
)

from .quant_scoring import (
    calculate_multi_factor_score,
    generate_quant_signals,
    QuantScore,
    MultiFactorModel,
)

__all__ = [
    # Stock data tools (Technical Analyst)
    'get_stock_history',
    'get_stock_news',
    'get_stock_technical_indicators',
    'get_industry_comparison',
    'analyze_stock_comprehensive',
    'get_northbound_flow',
    'get_dragon_tiger_board',
    # News analysis tools (News Analyst)
    'analyze_news_sentiment',
    'get_macroeconomic_indicators',
    'assess_event_impact',
    'get_global_market_news',
    # Sentiment tools (Sentiment Analyst)
    'analyze_social_media_sentiment',
    'get_public_sentiment_score',
    'track_market_mood',
    # Fundamentals tools (Fundamentals Analyst)
    'get_company_financials',
    'calculate_intrinsic_value',
    'get_performance_metrics',
    'identify_red_flags',
    # Tool Registry
    'ToolRegistry',
    'tool_registry',
    'init_tool_registry',
    'get_tool_registry',
    # Risk Metrics (Quantitative Analyst)
    'calculate_volatility',
    'calculate_beta',
    'calculate_max_drawdown',
    'calculate_sharpe_ratio',
    'calculate_var',
    # Quantitative Scoring
    'calculate_multi_factor_score',
    'generate_quant_signals',
    'QuantScore',
    'MultiFactorModel',
]
