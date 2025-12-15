"""
Sentiment Analysis Tools
情绪分析工具集

专为Sentiment Analyst设计的工具集，提供：
- 社交媒体情感分析
- 公众情绪评分
- 市场情绪追踪
"""

import akshare as ak
import pandas as pd
from langchain_core.tools import tool
from typing import Optional
import datetime


@tool
def analyze_social_media_sentiment(symbol: str) -> str:
    """
    分析社交媒体上关于该股票的情感倾向。
    
    通过分析股吧、论坛等社交平台的讨论，评估散户情绪。
    
    Args:
        symbol: 股票代码（6位数字）
        
    Returns:
        社交媒体情感分析结果
        
    Example:
        >>> result = analyze_social_media_sentiment.invoke({"symbol": "600519"})
    """
    try:
        # 获取股吧评论数据（东方财富）
        try:
            # 这里使用新闻数据作为情绪的代理指标
            # 实际应用中可以接入微博、雪球等API
            news_df = ak.stock_news_em(symbol=symbol)
            
            if news_df.empty:
                return f"未找到股票 {symbol} 的社交媒体数据"
            
            # 简化的情绪分析
            positive_words = ['看好', '买入', '持有', '上涨', '利好', '机会', '强势', '突破']
            negative_words = ['看空', '卖出', '下跌', '利空', '风险', '弱势', '跌破', '谨慎']
            
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            # 分析前20条新闻/评论
            for idx, row in news_df.head(20).iterrows():
                text = str(row.get('新闻标题', '')) + str(row.get('新闻内容', ''))
                
                pos = sum(1 for word in positive_words if word in text)
                neg = sum(1 for word in negative_words if word in text)
                
                if pos > neg:
                    positive_count += 1
                elif neg > pos:
                    negative_count += 1
                else:
                    neutral_count += 1
            
            total = positive_count + negative_count + neutral_count
            
            result = f"【股票 {symbol} 社交媒体情感分析】\n\n"
            result += f"分析样本数: {total}\n\n"
            result += f"情感分布:\n"
            result += f"  看多: {positive_count} ({positive_count/total*100:.1f}%)\n"
            result += f"  看空: {negative_count} ({negative_count/total*100:.1f}%)\n"
            result += f"  中性: {neutral_count} ({neutral_count/total*100:.1f}%)\n\n"
            
            # 计算情绪指数 (0-100)
            sentiment_index = (positive_count - negative_count) / total * 50 + 50
            
            result += f"【情绪指数】\n"
            result += f"综合情绪: {sentiment_index:.1f}/100\n"
            
            if sentiment_index > 65:
                mood = "乐观 😊"
                interpretation = "市场情绪偏乐观，散户看多情绪浓厚"
            elif sentiment_index > 45:
                mood = "中性 😐"
                interpretation = "市场情绪相对平稳，多空分歧不大"
            else:
                mood = "悲观 😟"
                interpretation = "市场情绪偏悲观，散户看空情绪较强"
            
            result += f"情绪判断: {mood}\n"
            result += f"解读: {interpretation}\n\n"
            
            result += f"【投资启示】\n"
            if sentiment_index > 75:
                result += "⚠️ 情绪过度乐观，需警惕追高风险\n"
            elif sentiment_index < 25:
                result += "💡 情绪过度悲观，可能存在反弹机会\n"
            else:
                result += "✓ 情绪处于合理区间\n"
            
            return result
            
        except Exception as e:
            return f"社交媒体情感分析失败: {str(e)}"
    
    except Exception as e:
        return f"社交媒体数据获取失败: {str(e)}"


@tool
def get_public_sentiment_score(symbol: str) -> str:
    """
    计算公众情绪评分。
    
    使用情感评分算法对公众情绪进行量化评估。
    
    Args:
        symbol: 股票代码（6位数字）
        
    Returns:
        情绪评分报告 (0-10分)
        
    Example:
        >>> result = get_public_sentiment_score.invoke({"symbol": "600519"})
    """
    try:
        # 获取新闻数据作为情绪代理
        news_df = ak.stock_news_em(symbol=symbol)
        
        if news_df.empty:
            return f"无法获取股票 {symbol} 的情绪数据"
        
        # 情绪关键词权重
        strong_positive = ['大涨', '暴涨', '创新高', '重大利好', '强烈推荐']
        positive = ['上涨', '增长', '利好', '看好', '机会']
        strong_negative = ['大跌', '暴跌', '创新低', '重大利空', '强烈看空']
        negative = ['下跌', '下滑', '利空', '风险', '谨慎']
        
        score = 5.0  # 基准分
        
        # 分析最近的新闻
        for idx, row in news_df.head(15).iterrows():
            text = str(row.get('新闻标题', '')) + str(row.get('新闻内容', ''))
            
            # 计算权重
            if any(word in text for word in strong_positive):
                score += 0.5
            elif any(word in text for word in positive):
                score += 0.2
            
            if any(word in text for word in strong_negative):
                score -= 0.5
            elif any(word in text for word in negative):
                score -= 0.2
        
        # 限制在0-10之间
        score = max(0, min(10, score))
        
        result = f"【股票 {symbol} 公众情绪评分】\n\n"
        result += f"情绪评分: {score:.1f}/10\n\n"
        
        # 评分解读
        if score >= 8:
            level = "极度乐观"
            emoji = "🔥"
            warning = "⚠️ 情绪过热，警惕回调风险"
        elif score >= 6.5:
            level = "乐观"
            emoji = "😊"
            warning = "✓ 情绪积极，但需关注基本面支撑"
        elif score >= 4.5:
            level = "中性"
            emoji = "😐"
            warning = "✓ 情绪平稳，观望为主"
        elif score >= 3:
            level = "悲观"
            emoji = "😟"
            warning = "💡 情绪低迷，可能存在机会"
        else:
            level = "极度悲观"
            emoji = "😱"
            warning = "💡 情绪冰点，关注反转信号"
        
        result += f"情绪等级: {level} {emoji}\n"
        result += f"风险提示: {warning}\n\n"
        
        result += f"【评分说明】\n"
        result += f"0-2分: 极度悲观 | 2-4分: 悲观 | 4-6分: 中性\n"
        result += f"6-8分: 乐观 | 8-10分: 极度乐观\n\n"
        
        result += f"【建议】\n"
        result += f"情绪是重要的市场指标，但不应作为唯一决策依据。\n"
        result += f"建议结合基本面、技术面进行综合判断。"
        
        return result
        
    except Exception as e:
        return f"公众情绪评分失败: {str(e)}"


@tool
def track_market_mood() -> str:
    """
    追踪整体市场情绪。
    
    分析大盘和市场整体的情绪状态，用于短期市场情绪判断。
    
    Returns:
        市场整体情绪报告
        
    Example:
        >>> result = track_market_mood.invoke({})
    """
    try:
        result = "【A股市场整体情绪追踪】\n\n"
        
        # 获取市场指数数据
        try:
            # 上证指数
            sh_index = ak.stock_zh_index_daily(symbol="sh000001")
            
            if not sh_index.empty:
                latest = sh_index.iloc[-1]
                prev = sh_index.iloc[-2]
                
                change = latest['close'] - prev['close']
                change_pct = (change / prev['close']) * 100
                
                result += f"【上证指数】\n"
                result += f"最新收盘: {latest['close']:.2f}\n"
                result += f"涨跌幅: {change_pct:+.2f}%\n\n"
                
                # 计算短期涨跌情况
                recent_5 = sh_index.tail(5)
                up_days = (recent_5['close'].diff() > 0).sum()
                
                result += f"【近5日表现】\n"
                result += f"上涨天数: {up_days}/5\n"
                
                # 市场情绪判断
                if change_pct > 1:
                    mood = "强势上涨 🚀"
                    sentiment = "乐观"
                elif change_pct > 0:
                    mood = "温和上涨 📈"
                    sentiment = "偏乐观"
                elif change_pct > -1:
                    mood = "温和下跌 📉"
                    sentiment = "偏谨慎"
                else:
                    mood = "大幅下跌 ⚠️"
                    sentiment = "谨慎"
                
                result += f"当日表现: {mood}\n"
                result += f"市场情绪: {sentiment}\n\n"
        except:
            result += "【上证指数】 数据获取失败\n\n"
        
        # 涨跌家数分析
        try:
            result += f"【市场广度】\n"
            result += f"涨跌家数比是衡量市场情绪的重要指标\n"
            result += f"建议关注涨停板数量、跌停板数量等数据\n\n"
        except:
            pass
        
        # 成交量分析
        try:
            if not sh_index.empty:
                latest_vol = sh_index.iloc[-1]['volume']
                avg_vol = sh_index.tail(20)['volume'].mean()
                
                vol_ratio = latest_vol / avg_vol
                
                result += f"【成交量】\n"
                result += f"量比: {vol_ratio:.2f}\n"
                
                if vol_ratio > 1.5:
                    vol_mood = "放量 (资金活跃)"
                elif vol_ratio > 0.8:
                    vol_mood = "正常 (成交适中)"
                else:
                    vol_mood = "缩量 (观望情绪浓)"
                
                result += f"量能判断: {vol_mood}\n\n"
        except:
            pass
        
        result += f"【投资建议】\n"
        result += f"• 市场情绪影响短期走势\n"
        result += f"• 极端情绪往往是转折信号\n"
        result += f"• 建议结合技术面和基本面判断\n"
        
        return result
        
    except Exception as e:
        return f"市场情绪追踪失败: {str(e)}"
