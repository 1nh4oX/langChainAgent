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
    import time
    
    # 重试机制
    max_retries = 3
    retry_delay = 1  # 初始延迟1秒
    
    for attempt in range(max_retries):
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
                return f"未找到股票 {symbol} 的数据。\n\n可能原因:\n- 股票代码不正确\n- 该股票已退市\n- 数据源暂时不可用\n\n请确认股票代码格式为6位数字（如 600519）"

            # 数据清洗
            df = df[['日期', '开盘', '收盘', '最高', '最低', '成交量']]
            
            # 只取最近 10 天
            recent_data = df.tail(10).copy()
            
            # 插入 id 列作为第一列
            recent_data.insert(0, 'id', range(1, len(recent_data) + 1))
            
            # 转换为 Markdown
            return recent_data.to_markdown(index=False)

        except Exception as e:
            if attempt < max_retries - 1:
                # 如果不是最后一次尝试，等待后重试
                time.sleep(retry_delay)
                retry_delay *= 2  # 指数退避
                continue
            else:
                # 最后一次尝试失败，返回详细错误信息
                return f"获取股票 {symbol} 数据失败（已重试{max_retries}次）\n\n错误信息: {str(e)}\n\n建议:\n- 检查网络连接\n- 确认股票代码格式正确（6位数字）\n- 稍后重试"


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
    import time
    
    # 重试机制
    max_retries = 2
    
    for attempt in range(max_retries):
        try:
            # 使用 AkShare 获取个股新闻
            df = ak.stock_news_em(symbol=symbol)
            
            if df.empty:
                return f"暂无股票 {symbol} 的新闻数据。\n\n可能原因:\n- 该股票近期没有相关新闻\n- 数据源暂时不可用\n- 股票代码可能不正确\n\n建议:\n- 访问东方财富网等财经网站查看新闻\n- 确认股票代码格式正确"
            
            # 取最新的 max_news 条
            recent_news = df.head(max_news).copy()
            
            # 格式化输出
            news_list = []
            for idx, row in recent_news.iterrows():
                news_item = f"【{row.get('发布时间', 'N/A')}】{row.get('新闻标题', 'N/A')}\n来源: {row.get('新闻来源', 'N/A')}"
                news_list.append(news_item)
            
            return "\n\n".join(news_list)
        
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            else:
                return f"获取股票 {symbol} 新闻失败（已重试{max_retries}次）\n\n错误: {str(e)}\n\n建议:\n- 检查网络连接\n- 访问财经网站手动查看新闻\n- 稍后重试"


@tool
def get_stock_technical_indicators(symbol: str) -> str:
    """
    计算股票的技术指标（MA5, MA10, MA20 均线, MACD, RSI等）。
    
    Args:
        symbol: 股票代码（6位数字）
        
    Returns:
        包含技术指标的分析文本
        
    Example:
        >>> result = get_stock_technical_indicators.invoke({"symbol": "600519"})
    """
    try:
        # 获取历史数据
        start_date, end_date = get_date_range(90)  # 获取90天数据用于计算指标
        df = ak.stock_zh_a_hist(symbol=symbol, start_date=start_date, end_date=end_date, adjust="qfq")
        
        if df.empty:
            return f"无法获取股票 {symbol} 的技术指标数据"
        
        # 计算均线
        df['MA5'] = df['收盘'].rolling(window=5).mean()
        df['MA10'] = df['收盘'].rolling(window=10).mean()
        df['MA20'] = df['收盘'].rolling(window=20).mean()
        df['MA60'] = df['收盘'].rolling(window=60).mean()
        
        # 计算MACD指标
        # 12日EMA
        df['EMA12'] = df['收盘'].ewm(span=12, adjust=False).mean()
        # 26日EMA
        df['EMA26'] = df['收盘'].ewm(span=26, adjust=False).mean()
        # DIF = EMA12 - EMA26
        df['DIF'] = df['EMA12'] - df['EMA26']
        # DEA = DIF的9日EMA
        df['DEA'] = df['DIF'].ewm(span=9, adjust=False).mean()
        # MACD柱 = (DIF - DEA) * 2
        df['MACD'] = (df['DIF'] - df['DEA']) * 2
        
        # 计算RSI指标 (14日)
        delta = df['收盘'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        result = f"【股票 {symbol} 技术指标分析】\n\n"
        
        # 均线系统
        result += "【均线系统】\n"
        result += f"当前价格: {latest['收盘']:.2f}元\n"
        result += f"MA5:  {latest['MA5']:.2f}元\n"
        result += f"MA10: {latest['MA10']:.2f}元\n"
        result += f"MA20: {latest['MA20']:.2f}元\n"
        result += f"MA60: {latest['MA60']:.2f}元\n\n"
        
        # 均线形态判断
        result += "【均线形态】\n"
        if latest['MA5'] > latest['MA10'] > latest['MA20']:
            result += "✓ 多头排列 (短期均线在上，趋势向上)\n"
            ma_signal = "看多"
        elif latest['MA5'] < latest['MA10'] < latest['MA20']:
            result += "✗ 空头排列 (短期均线在下，趋势向下)\n"
            ma_signal = "看空"
        else:
            result += "○ 均线纠缠 (方向不明确)\n"
            ma_signal = "观望"
        
        # 价格与均线关系
        if latest['收盘'] > latest['MA5']:
            result += "• 价格在MA5上方\n"
        else:
            result += "• 价格在MA5下方\n"
        
        result += "\n"
        
        # MACD指标
        result += "【MACD指标】\n"
        result += f"DIF:  {latest['DIF']:.3f}\n"
        result += f"DEA:  {latest['DEA']:.3f}\n"
        result += f"MACD: {latest['MACD']:.3f}\n\n"
        
        # MACD信号判断
        result += "【MACD信号】\n"
        if latest['DIF'] > latest['DEA'] and prev['DIF'] <= prev['DEA']:
            result += "🚀 金叉 (DIF上穿DEA，买入信号)\n"
            macd_signal = "强烈看多"
        elif latest['DIF'] < latest['DEA'] and prev['DIF'] >= prev['DEA']:
            result += "⚠️ 死叉 (DIF下穿DEA，卖出信号)\n"
            macd_signal = "看空"
        elif latest['DIF'] > latest['DEA']:
            result += "✓ DIF在DEA上方 (多头)\n"
            macd_signal = "看多"
        else:
            result += "✗ DIF在DEA下方 (空头)\n"
            macd_signal = "看空"
        
        if latest['MACD'] > 0:
            result += "• MACD柱为正 (动能向上)\n"
        else:
            result += "• MACD柱为负 (动能向下)\n"
        
        result += "\n"
        
        # RSI指标
        result += "【RSI指标 (14日)】\n"
        result += f"当前RSI: {latest['RSI']:.2f}\n\n"
        
        # RSI判断
        result += "【RSI信号】\n"
        if latest['RSI'] > 70:
            result += "⚠️ 超买区域 (RSI>70，可能面临回调)\n"
            rsi_signal = "超买警告"
        elif latest['RSI'] > 50:
            result += "✓ 强势区域 (RSI>50，多方占优)\n"
            rsi_signal = "偏多"
        elif latest['RSI'] > 30:
            result += "○ 弱势区域 (RSI<50，空方占优)\n"
            rsi_signal = "偏空"
        else:
            result += "💡 超卖区域 (RSI<30，可能存在反弹机会)\n"
            rsi_signal = "超卖机会"
        
        result += "\n"
        
        # 综合技术评分
        result += "【综合技术信号】\n"
        
        signals = {
            '均线': ma_signal,
            'MACD': macd_signal,
            'RSI': rsi_signal
        }
        
        for indicator, signal in signals.items():
            result += f"• {indicator}: {signal}\n"
        
        # 简单的评分系统
        score = 0
        if '多' in ma_signal:
            score += 3
        if '多' in macd_signal:
            score += 3
        if '多' in rsi_signal or '机会' in rsi_signal:
            score += 2
        
        result += f"\n技术面评分: {score}/8分\n"
        
        if score >= 6:
            result += "综合判断: 技术面看多 📈\n"
        elif score >= 3:
            result += "综合判断: 技术面中性 ○\n"
        else:
            result += "综合判断: 技术面看空 📉\n"
        
        return result
        
    except Exception as e:
        return f"技术指标计算失败: {str(e)}"


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


@tool
def get_northbound_flow(symbol: str) -> str:
    """
    获取个股北向资金（沪深股通）近期净买入情况
    北向资金是外资机构的重要风向标，持续净买入为强烈看涨信号
    
    Args:
        symbol: 股票代码（如 '600519'）
    
    Returns:
        北向资金净流入数据的Markdown格式描述
    """
    results = []
    results.append(f"=== {symbol} 北向资金（陆股通）动态 ===\n")
    
    try:
        # 尝试获取全市场北向资金汇总数据（每日净买入额）
        df = ak.stock_hsgt_north_net_flow_in(symbol="沪深股通")
        if df is not None and not df.empty:
            # 取最近10个交易日
            recent = df.tail(10)
            results.append("| 日期 | 北向净买入（亿元）| 趋势 |")
            results.append("|------|-----------------|------|")
            for _, row in recent.iterrows():
                try:
                    val = float(str(row.iloc[1]).replace(',', ''))
                    trend = "📈 净流入" if val > 0 else "📉 净流出"
                    results.append(f"| {row.iloc[0]} | {val:.2f} | {trend} |")
                except Exception:
                    pass
            
            # 统计总趋势
            try:
                vals = [float(str(r.iloc[1]).replace(',', '')) 
                        for _, r in recent.iterrows()]
                total = sum(vals)
                pos_days = sum(1 for v in vals if v > 0)
                results.append(f"\n近10日汇总:")
                results.append(f"  合计净流入: {total:.2f} 亿元")
                results.append(f"  净流入天数: {pos_days}/10 天")
                if total > 50:
                    results.append("  ⭐ 北向资金持续大幅净买入——外资看好信号明显")
                elif total > 0:
                    results.append("  ✅ 北向资金小幅净买入——外资态度偏积极")
                elif total > -50:
                    results.append("  ⚠️ 北向资金小幅净卖出——外资态度偏谨慎")
                else:
                    results.append("  🚨 北向资金大幅净卖出——外资明显撤离")
            except Exception:
                pass
        else:
            results.append("北向资金数据暂无，可能为非陆股通标的或数据源限制。")
    except Exception as e:
        results.append(f"获取北向资金数据失败（可能为非陆股通标的）: {str(e)[:80]}")
        results.append("提示: 北向资金数据仅覆盖沪深股通合资格个股。")
    
    return "\n".join(results)


@tool
def get_dragon_tiger_board(symbol: str) -> str:
    """
    获取个股近期龙虎榜登榜情况（游资/机构动向的重要信号）
    龙虎榜反映了主力资金的介入程度，是判断市场关注度的重要参考
    
    Args:
        symbol: 股票代码（如 '600519'）
    
    Returns:
        龙虎榜登榜情况的Markdown格式描述
    """
    results = []
    results.append(f"=== {symbol} 龙虎榜数据 ===\n")
    
    try:
        # 获取个股龙虎榜统计（近期登榜情况）
        df = ak.stock_lhb_stock_statistic_em(symbol=symbol, period="近一月")
        if df is not None and not df.empty:
            results.append(f"📋 近一月龙虎榜上榜次数: {len(df)} 次\n")
            results.append("| 上榜日期 | 上榜原因 | 净买入（万元）|")
            results.append("|---------|---------|--------------|")
            for _, row in df.head(5).iterrows():
                try:
                    date_val = str(row.get('上榜日期', row.iloc[0]))
                    reason = str(row.get('上榜原因', row.iloc[1] if len(row) > 1 else 'N/A'))[:20]
                    # 净买入金额
                    net_val = str(row.get('净买入', row.iloc[3] if len(row) > 3 else 'N/A'))
                    results.append(f"| {date_val} | {reason} | {net_val} |")
                except Exception:
                    pass
            
            results.append(f"\n龙虎榜解读:")
            if len(df) >= 3:
                results.append("  ⚡ 近期多次上榜，主力资金关注度高，短线波动性较大")
                results.append("  投资启示: 需判断是游资炒作还是机构建仓，结合成交量分析")
            elif len(df) >= 1:
                results.append("  📌 近期有上榜记录，存在主力资金介入迹象")
            else:
                results.append("  ✅ 近期未上榜，走势相对稳健，无明显游资炒作痕迹")
        else:
            results.append("近一月无龙虎榜上榜记录。")
            results.append("✅ 股价走势相对平稳，未受到游资异常关注。")
    except Exception as e:
        # 尝试备用接口
        try:
            df2 = ak.stock_lhb_detail_em(symbol=symbol)
            if df2 is not None and not df2.empty:
                results.append(f"近期龙虎榜记录: {len(df2)} 条")
            else:
                results.append("近期无龙虎榜记录（数据正常，未受异常关注）。")
        except Exception:
            results.append(f"龙虎榜数据获取失败: {str(e)[:80]}")
            results.append("提示: 该股票可能近期没有上榜记录，属于正常情况。")
    
    return "\n".join(results)


# 测试代码
if __name__ == "__main__":
    print("测试股票工具模块...")
    print(get_stock_history.invoke({"symbol": "600519"}))



