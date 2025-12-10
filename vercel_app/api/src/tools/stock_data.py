"""
Stock Data Tools
股票数据获取和分析工具集

该模块提供以下工具：
- get_stock_history: 获取历史行情数据
- get_stock_news: 获取新闻资讯
- get_stock_technical_indicators: 计算技术指标
- get_industry_comparison: 行业对比分析
- analyze_stock_comprehensive: 综合分析
"""

import akshare as ak
import pandas as pd
from langchain_core.tools import tool
import datetime
from typing import Optional


def get_current_date() -> str:
    """获取今天的日期字符串"""
    return datetime.datetime.now().strftime("%Y%m%d")


def get_date_range(days: int = 30) -> tuple:
    """
    获取日期范围
    
    Args:
        days: 天数
    
    Returns:
        (start_date, end_date) 格式为 YYYYMMDD
    """
    end_date = datetime.datetime.now().strftime("%Y%m%d")
    start_date = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%Y%m%d")
    return start_date, end_date


@tool
def get_stock_history(symbol: str) -> str:
    """
    获取中国A股股票的近期历史行情数据。
    
    Args:
        symbol: 股票代码，必须是6位数字（例如：'600519' 代表贵州茅台, '000001' 代表平安银行）
        
    Returns:
        包含日期、开盘、收盘、最高、最低、成交量的表格文本
        
    Example:
        >>> result = get_stock_history.invoke({"symbol": "600519"})
    """
    # print(f"\n[工具调用] 正在从 AkShare 获取 {symbol} 的数据...")
    
    try:
        # 设定开始时间为 1 个月前
        start_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y%m%d")
        end_date = get_current_date()

        # 调用 AkShare 接口：stock_zh_a_hist (A股日频率数据)
        # period="daily" 日线
        # adjust="qfq" 前复权 (分析价格趋势通常用前复权)
        df = ak.stock_zh_a_hist(
            symbol=symbol, 
            period="daily", 
            start_date=start_date, 
            end_date=end_date, 
            adjust="qfq"
        )
        
        if df.empty:
            return "未找到该股票数据，请确认代码是否正确。"

        # 数据清洗
        df = df[['日期', '开盘', '收盘', '最高', '最低', '成交量']]
        
        # 只取最近 10 天
        recent_data = df.tail(10).copy()
        
        # 插入 id 列作为第一列
        recent_data.insert(0, 'id', range(1, len(recent_data) + 1))
        
        # 转换为 Markdown
        return recent_data.to_markdown(index=False)

    except Exception as e:
        return f"获取数据失败: {str(e)}"


@tool
def get_stock_news(symbol: str, max_news: int = 10) -> str:
    """
    获取指定股票的最新新闻资讯。
    
    Args:
        symbol: 股票代码（6位数字）
        max_news: 返回的新闻条数，默认10条
        
    Returns:
        包含新闻标题、发布时间、来源的文本
        
    Example:
        >>> result = get_stock_news.invoke({"symbol": "600519", "max_news": 5})
    """
    # print(f"\n[工具调用] 正在获取 {symbol} 的新闻资讯...")
    
    try:
        # 使用 AkShare 获取个股新闻
        df = ak.stock_news_em(symbol=symbol)
        
        if df.empty:
            return "暂无该股票的新闻数据。"
        
        # 取最新的 max_news 条
        recent_news = df.head(max_news).copy()
        
        # 格式化输出
        news_list = []
        for idx, row in recent_news.iterrows():
            news_item = f"【{row.get('发布时间', 'N/A')}】{row.get('新闻标题', 'N/A')}\n来源: {row.get('新闻来源', 'N/A')}"
            news_list.append(news_item)
        
        return "\n\n".join(news_list)
    
    except Exception as e:
        return f"获取新闻失败: {str(e)}"


@tool
def get_stock_technical_indicators(symbol: str) -> str:
    """
    计算股票的技术指标（MA5, MA10, MA20 均线，涨跌幅等）。
    
    Args:
        symbol: 股票代码（6位数字）
        
    Returns:
        包含技术指标的分析文本
        
    Example:
        >>> result = get_stock_technical_indicators.invoke({"symbol": "600519"})
    """
    # print(f"\n[工具调用] 正在计算 {symbol} 的技术指标...")
    
    try:
        start_date, end_date = get_date_range(60)
        df = ak.stock_zh_a_hist(
            symbol=symbol, 
            period="daily", 
            start_date=start_date, 
            end_date=end_date, 
            adjust="qfq"
        )
        
        if df.empty or len(df) < 20:
            return "数据不足，无法计算技术指标。"
        
        # 计算均线
        df['MA5'] = df['收盘'].rolling(window=5).mean()
        df['MA10'] = df['收盘'].rolling(window=10).mean()
        df['MA20'] = df['收盘'].rolling(window=20).mean()
        
        # 获取最新数据
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # 计算涨跌幅
        change_pct = ((latest['收盘'] - prev['收盘']) / prev['收盘']) * 100
        
        # 判断均线趋势
        ma_trend = "多头排列" if latest['MA5'] > latest['MA10'] > latest['MA20'] else \
                   "空头排列" if latest['MA5'] < latest['MA10'] < latest['MA20'] else "震荡"
        
        result = f"""技术指标分析 ({latest['日期']}):
- 最新收盘价: {latest['收盘']:.2f} 元
- 涨跌幅: {change_pct:+.2f}%
- MA5: {latest['MA5']:.2f} 元
- MA10: {latest['MA10']:.2f} 元  
- MA20: {latest['MA20']:.2f} 元
- 均线趋势: {ma_trend}
- 成交量: {latest['成交量']} 手
"""
        return result
        
    except Exception as e:
        return f"计算技术指标失败: {str(e)}"


@tool
def get_industry_comparison(symbol: str) -> str:
    """
    获取股票所属行业的表现对比。
    
    Args:
        symbol: 股票代码（6位数字）
        
    Returns:
        行业板块信息和对比数据
        
    Example:
        >>> result = get_industry_comparison.invoke({"symbol": "600519"})
    """
    # print(f"\n[工具调用] 正在获取 {symbol} 的行业对比数据...")
    
    try:
        # 获取股票基本信息
        stock_info = ak.stock_individual_info_em(symbol=symbol)
        
        if stock_info.empty:
            return "无法获取股票基本信息。"
        
        # 提取关键信息
        info_dict = dict(zip(stock_info['item'], stock_info['value']))
        
        result = f"""股票基本信息:
- 股票名称: {info_dict.get('股票简称', 'N/A')}
- 所属行业: {info_dict.get('行业', 'N/A')}
- 总市值: {info_dict.get('总市值', 'N/A')}
- 流通市值: {info_dict.get('流通市值', 'N/A')}
- 市盈率: {info_dict.get('市盈率-动态', 'N/A')}
- 市净率: {info_dict.get('市净率', 'N/A')}
"""
        return result
        
    except Exception as e:
        return f"获取行业信息失败: {str(e)}"


@tool
def analyze_stock_comprehensive(symbol: str) -> str:
    """
    综合分析工具：一次性获取股票的历史数据、技术指标、基本面信息。
    这是一个高级工具，适合需要全面了解某只股票时使用。
    
    Args:
        symbol: 股票代码（6位数字）
        
    Returns:
        综合分析报告
        
    Example:
        >>> result = analyze_stock_comprehensive.invoke({"symbol": "600519"})
    """
    # print(f"\n[工具调用] 正在进行 {symbol} 的综合分析...")
    
    results = []
    results.append("=" * 50)
    results.append("综合分析报告")
    results.append("=" * 50)
    
    # 1. 基本信息
    try:
        stock_info = ak.stock_individual_info_em(symbol=symbol)
        info_dict = dict(zip(stock_info['item'], stock_info['value']))
        results.append(f"\n📊 股票: {info_dict.get('股票简称', symbol)}")
        results.append(f"行业: {info_dict.get('行业', 'N/A')}")
    except:
        results.append(f"\n📊 股票代码: {symbol}")
    
    # 2. 最新行情
    try:
        start_date, end_date = get_date_range(5)
        df = ak.stock_zh_a_hist(
            symbol=symbol, 
            period="daily", 
            start_date=start_date, 
            end_date=end_date, 
            adjust="qfq"
        )
        if not df.empty:
            latest = df.iloc[-1]
            results.append(f"\n💰 最新价格: {latest['收盘']:.2f} 元")
            results.append(f"成交量: {latest['成交量']} 手")
    except:
        pass
    
    return "\n".join(results)


# 测试代码
if __name__ == "__main__":
    print("测试股票工具模块...")
    print(get_stock_history.invoke({"symbol": "600519"}))



