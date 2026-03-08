"""
Tool Registry Module
工具注册表模块

提供统一的工具管理，支持:
- 工具注册和分类
- 按类别获取工具
- 为ReAct Agent提供工具列表
"""

from typing import List, Dict, Optional
from langchain_core.tools import BaseTool


class ToolRegistry:
    """工具注册表 - 管理所有可用工具"""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._categories: Dict[str, List[str]] = {
            "fundamentals": [],  # 基本面分析工具
            "technical": [],     # 技术分析工具
            "sentiment": [],     # 情绪分析工具
            "news": [],          # 新闻分析工具
            "general": []        # 通用工具
        }
        self._tool_descriptions: Dict[str, str] = {}
    
    def register(self, tool: BaseTool, category: str = "general", description: Optional[str] = None):
        """
        注册工具到注册表
        
        Args:
            tool: LangChain工具对象
            category: 工具类别
            description: 工具描述（可选，默认使用工具自带描述）
        """
        self._tools[tool.name] = tool
        
        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(tool.name)
        
        # 存储描述
        self._tool_descriptions[tool.name] = description or tool.description
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """获取单个工具"""
        return self._tools.get(name)
    
    def get_tools_by_category(self, category: str) -> List[BaseTool]:
        """按类别获取工具列表"""
        tool_names = self._categories.get(category, [])
        return [self._tools[name] for name in tool_names if name in self._tools]
    
    def get_all_tools(self) -> List[BaseTool]:
        """获取所有注册的工具"""
        return list(self._tools.values())
    
    def get_tools_for_role(self, role: str) -> List[BaseTool]:
        """
        根据Agent角色获取推荐的工具列表
        
        Args:
            role: Agent角色标识
            
        Returns:
            推荐的工具列表
        """
        role_tool_mapping = {
            "fundamentals_analyst": ["fundamentals", "general"],
            "technical_analyst": ["technical", "general"],
            "sentiment_analyst": ["sentiment", "general"],
            "news_analyst": ["news", "general"],
            "trader": ["fundamentals", "technical", "sentiment", "news"],
            "portfolio_manager": ["fundamentals", "technical", "sentiment", "news"],
        }
        
        categories = role_tool_mapping.get(role, ["general"])
        tools = []
        for cat in categories:
            tools.extend(self.get_tools_by_category(cat))
        
        # 去重
        seen = set()
        unique_tools = []
        for tool in tools:
            if tool.name not in seen:
                seen.add(tool.name)
                unique_tools.append(tool)
        
        return unique_tools
    
    def list_all(self) -> Dict[str, List[str]]:
        """列出所有工具及其类别"""
        return {
            category: [
                f"{name}: {self._tool_descriptions.get(name, 'No description')[:50]}..."
                for name in tool_names
            ]
            for category, tool_names in self._categories.items()
            if tool_names
        }


# 全局注册表实例
tool_registry = ToolRegistry()


def init_tool_registry():
    """
    初始化并注册所有工具
    
    在应用启动时调用此函数以注册所有可用工具
    """
    from src.tools import (
        # Fundamentals tools
        get_company_financials,
        calculate_intrinsic_value,
        get_performance_metrics,
        identify_red_flags,
        # Technical tools
        get_stock_history,
        get_stock_technical_indicators,
        get_industry_comparison,
        analyze_stock_comprehensive,
        # Sentiment tools
        analyze_social_media_sentiment,
        get_public_sentiment_score,
        track_market_mood,
        # News tools
        analyze_news_sentiment,
        get_macroeconomic_indicators,
        assess_event_impact,
        get_global_market_news,
    )
    
    # 注册基本面分析工具
    tool_registry.register(
        get_company_financials, 
        "fundamentals",
        "获取公司财务报表数据，包括资产负债表、利润表、现金流量表的关键指标"
    )
    tool_registry.register(
        calculate_intrinsic_value,
        "fundamentals", 
        "计算股票的内在价值评估，基于财务数据和估值模型"
    )
    tool_registry.register(
        get_performance_metrics,
        "fundamentals",
        "获取公司业绩指标，包括PE、ROE、营收增长等"
    )
    tool_registry.register(
        identify_red_flags,
        "fundamentals",
        "识别公司财务风险信号，分析财务报表中的异常指标"
    )
    
    # 注册技术分析工具
    tool_registry.register(
        get_stock_history,
        "technical",
        "获取股票近期历史行情数据，包括日期、开盘、收盘、最高、最低、成交量"
    )
    tool_registry.register(
        get_stock_technical_indicators,
        "technical",
        "计算股票技术指标，包括MA均线、MACD、RSI等"
    )
    tool_registry.register(
        get_industry_comparison,
        "technical",
        "获取股票所属行业的表现对比"
    )
    tool_registry.register(
        analyze_stock_comprehensive,
        "general",
        "综合分析工具，一次性获取股票的历史数据、技术指标、基本面信息"
    )
    
    # 注册情绪分析工具
    tool_registry.register(
        analyze_social_media_sentiment,
        "sentiment",
        "分析社交媒体上关于股票的情感倾向"
    )
    tool_registry.register(
        get_public_sentiment_score,
        "sentiment",
        "计算公众情绪评分(0-10分)"
    )
    tool_registry.register(
        track_market_mood,
        "sentiment",
        "追踪A股市场整体情绪状态"
    )
    
    # 注册新闻分析工具
    tool_registry.register(
        analyze_news_sentiment,
        "news",
        "分析与股票相关的新闻情感"
    )
    tool_registry.register(
        get_macroeconomic_indicators,
        "news",
        "获取宏观经济指标（PMI、CPI等）"
    )
    tool_registry.register(
        assess_event_impact,
        "news",
        "评估重大事件对股票的影响"
    )
    tool_registry.register(
        get_global_market_news,
        "news",
        "获取全球市场动态新闻"
    )
    
    return tool_registry


def get_tool_registry() -> ToolRegistry:
    """获取全局工具注册表实例"""
    return tool_registry
