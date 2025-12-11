"""
Stock Analysis Tools Module
股票分析工具模块
"""

from .stock_data import (
    get_stock_history,
    get_stock_news,
    get_stock_technical_indicators,
    get_industry_comparison,
    analyze_stock_comprehensive
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

__all__ = [
    # Stock data tools (Technical Analyst)
    'get_stock_history',
    'get_stock_news',
    'get_stock_technical_indicators',
    'get_industry_comparison',
    'analyze_stock_comprehensive',
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
]
