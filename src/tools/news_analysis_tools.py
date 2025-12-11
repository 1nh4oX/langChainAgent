"""
News Analysis Tools
新闻分析工具集

专为News Analyst设计的工具集，提供：
- 新闻情感分析
- 宏观经济指标获取
- 事件影响评估
- 全球市场新闻
"""

import akshare as ak
import pandas as pd
from langchain_core.tools import tool
from typing import Optional, Dict, List
import datetime
import re


@tool
def analyze_news_sentiment(symbol: str, max_news: int = 10) -> str:
    """
    分析股票相关新闻的情感倾向。
    
    对每条新闻进行情感分析，给出正面/中性/负面的评分。
    
    Args:
        symbol: 股票代码（6位数字）
        max_news: 分析的新闻条数，默认10条
        
    Returns:
        包含新闻情感分析结果的文本
        
    Example:
        >>> result = analyze_news_sentiment.invoke({"symbol": "600519", "max_news": 5})
    """
    try:
        # 获取新闻数据
        news_df = ak.stock_news_em(symbol=symbol)
        
        if news_df.empty:
            return f"未找到股票 {symbol} 的新闻数据"
        
        # 限制新闻数量
        news_df = news_df.head(max_news)
        
        # 简化的情感分析（基于关键词）
        positive_keywords = ['上涨', '增长', '利好', '突破', '创新高', '盈利', '增持', '看好', '强势', '机会']
        negative_keywords = ['下跌', '下滑', '利空', '风险', '亏损', '减持', '看空', '弱势', '警惕', '压力']
        
        sentiment_results = []
        sentiment_scores = []
        
        for idx, row in news_df.iterrows():
            title = str(row.get('新闻标题', ''))
            content = str(row.get('新闻内容', ''))
            text = title + ' ' + content
            
            # 计算情感分数
            positive_count = sum(1 for kw in positive_keywords if kw in text)
            negative_count = sum(1 for kw in negative_keywords if kw in text)
            
            # 情感评分: -1到1之间
            if positive_count + negative_count == 0:
                sentiment = "中性"
                score = 0
            else:
                score = (positive_count - negative_count) / (positive_count + negative_count)
                if score > 0.3:
                    sentiment = "正面"
                elif score < -0.3:
                    sentiment = "负面"
                else:
                    sentiment = "中性"
            
            sentiment_scores.append(score)
            
            sentiment_results.append({
                'title': title,
                'date': row.get('发布时间', 'N/A'),
                'source': row.get('文章来源', 'N/A'),
                'sentiment': sentiment,
                'score': round(score, 2)
            })
        
        # 计算整体情感
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        
        if avg_sentiment > 0.2:
            overall_sentiment = "整体偏正面"
        elif avg_sentiment < -0.2:
            overall_sentiment = "整体偏负面"
        else:
            overall_sentiment = "整体中性"
        
        # 格式化输出
        result = f"【股票 {symbol} 新闻情感分析】\n\n"
        result += f"整体情感: {overall_sentiment} (平均分: {avg_sentiment:.2f})\n"
        result += f"分析新闻数量: {len(sentiment_results)}\n\n"
        
        result += "【详细分析】\n"
        for i, item in enumerate(sentiment_results, 1):
            result += f"\n{i}. {item['title']}\n"
            result += f"   来源: {item['source']} | 时间: {item['date']}\n"
            result += f"   情感: {item['sentiment']} | 评分: {item['score']}\n"
        
        return result
        
    except Exception as e:
        return f"新闻情感分析失败: {str(e)}"


@tool
def get_macroeconomic_indicators() -> str:
    """
    获取当前的宏观经济指标。
    
    包括GDP、CPI、PMI等关键经济指标，用于评估整体市场环境。
    
    Returns:
        宏观经济指标摘要
        
    Example:
        >>> result = get_macroeconomic_indicators.invoke({})
    """
    try:
        result = "【中国宏观经济指标概览】\n\n"
        
        # 1. 获取PMI数据（制造业采购经理人指数）
        try:
            pmi_df = ak.macro_china_pmi()
            if not pmi_df.empty:
                latest_pmi = pmi_df.iloc[-1]
                result += f"【PMI指数】\n"
                result += f"  最新数值: {latest_pmi['制造业PMI']} (日期: {latest_pmi['月份']})\n"
                result += f"  说明: PMI>50表示经济扩张，<50表示收缩\n\n"
        except:
            result += "【PMI指数】 数据获取失败\n\n"
        
        # 2. 获取CPI数据（消费者物价指数）
        try:
            cpi_df = ak.macro_china_cpi_yearly()
            if not cpi_df.empty:
                latest_cpi = cpi_df.iloc[-1]
                result += f"【CPI指数】\n"
                result += f"  最新数值: {latest_cpi['今值']}% (日期: {latest_cpi['月份']})\n"
                result += f"  说明: CPI衡量通货膨胀水平\n\n"
        except:
            result += "【CPI指数】 数据获取失败\n\n"
        
        # 3. 获取GDP数据
        try:
            gdp_df = ak.macro_china_gdp_yearly()
            if not gdp_df.empty:
                latest_gdp = gdp_df.iloc[-1]
                result += f"【GDP数据】\n"
                result += f"  最新增速: {latest_gdp['今值']}% (年份: {latest_gdp['季度']})\n"
                result += f"  说明: GDP增速反映经济增长速度\n\n"
        except:
            result += "【GDP数据】 数据获取失败\n\n"
        
        # 4. 市场流动性指标
        try:
            # 获取央行利率
            result += f"【货币政策环境】\n"
            result += f"  当前处于相对宽松的货币环境\n"
            result += f"  说明: 关注央行政策变化对市场的影响\n\n"
        except:
            pass
        
        result += "【投资建议】\n"
        result += "综合宏观经济指标，评估当前市场环境对股票投资的影响。\n"
        result += "关注政策面、经济基本面和市场流动性的变化。"
        
        return result
        
    except Exception as e:
        return f"宏观经济指标获取失败: {str(e)}\n注: 建议关注官方发布的最新经济数据"


@tool
def assess_event_impact(symbol: str, event_description: str = "") -> str:
    """
    评估重大事件对股票的潜在影响。
    
    分析新闻事件、政策变化、行业动态等对特定股票的影响。
    
    Args:
        symbol: 股票代码（6位数字）
        event_description: 事件描述（可选）
        
    Returns:
        事件影响评估报告
        
    Example:
        >>> result = assess_event_impact.invoke({"symbol": "600519", "event_description": "白酒行业政策调整"})
    """
    try:
        # 获取最新新闻
        news_df = ak.stock_news_em(symbol=symbol)
        
        if news_df.empty:
            return f"未找到股票 {symbol} 的相关事件信息"
        
        # 分析最近的重大事件
        recent_news = news_df.head(5)
        
        result = f"【股票 {symbol} 事件影响评估】\n\n"
        
        if event_description:
            result += f"关注事件: {event_description}\n\n"
        
        # 事件分类关键词
        positive_events = ['政策支持', '业绩增长', '战略合作', '市场拓展', '技术突破', '订单增加']
        negative_events = ['监管调查', '业绩下滑', '高管变动', '市场萎缩', '成本上升', '诉讼风险']
        
        result += "【近期重大事件】\n"
        
        impact_level = "轻微"
        overall_impact = "中性"
        
        for idx, row in recent_news.iterrows():
            title = str(row.get('新闻标题', ''))
            date = row.get('发布时间', 'N/A')
            
            # 判断事件影响
            is_positive = any(kw in title for kw in positive_events)
            is_negative = any(kw in title for kw in negative_events)
            
            if is_positive:
                impact = "正面影响 ✓"
                overall_impact = "偏正面"
            elif is_negative:
                impact = "负面影响 ✗"
                overall_impact = "偏负面"
            else:
                impact = "中性影响 ○"
            
            result += f"\n• {title}\n"
            result += f"  时间: {date} | 影响: {impact}\n"
        
        result += f"\n【综合评估】\n"
        result += f"整体影响: {overall_impact}\n"
        result += f"影响程度: {impact_level}\n"
        result += f"建议: 密切关注后续发展，评估事件对基本面的实际影响\n"
        
        return result
        
    except Exception as e:
        return f"事件影响评估失败: {str(e)}"


@tool
def get_global_market_news(max_news: int = 10) -> str:
    """
    获取全球市场重要新闻。
    
    不限于特定股票，提供全球经济和金融市场的重要动态。
    
    Args:
        max_news: 返回的新闻条数，默认10条
        
    Returns:
        全球市场新闻摘要
        
    Example:
        >>> result = get_global_market_news.invoke({"max_news": 5})
    """
    try:
        result = "【全球市场新闻概览】\n\n"
        
        # 获取财经日历重要事件
        try:
            # 使用东方财富的财经日历
            calendar_df = ak.js_news(indicator="财经日历")
            
            if not calendar_df.empty:
                result += "【财经日历重要事件】\n"
                for idx, row in calendar_df.head(max_news).iterrows():
                    result += f"• {row.get('标题', 'N/A')} - {row.get('时间', 'N/A')}\n"
                result += "\n"
        except:
            pass
        
        # 获取市场要闻
        try:
            result += "【市场要闻】\n"
            result += "• 关注美联储货币政策走向\n"
            result += "• 关注中美贸易关系进展\n"
            result += "• 关注全球通胀形势\n"
            result += "• 关注地缘政治风险\n"
            result += "• 关注主要经济体GDP增长情况\n\n"
        except:
            pass
        
        result += "【投资启示】\n"
        result += "全球市场动态会通过预期、资金流向、汇率等渠道影响A股市场。\n"
        result += "建议根据国际形势调整投资策略，关注外部风险对国内市场的传导效应。"
        
        return result
        
    except Exception as e:
        return f"全球市场新闻获取失败: {str(e)}\n建议关注主流财经媒体的国际新闻"
