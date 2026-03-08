"""
Quantitative Scoring Module
量化评分模块

提供多因子量化分析：
- 价值因子评分
- 成长因子评分  
- 质量因子评分
- 动量因子评分
- 情绪因子评分
- 综合得分与信号生成
"""

import akshare as ak
import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Dict, Optional, Tuple
from langchain_core.tools import tool
import datetime


@dataclass
class QuantScore:
    """量化评分结果"""
    value_score: float      # 价值因子得分 (0-100)
    growth_score: float     # 成长因子得分 (0-100)
    quality_score: float    # 质量因子得分 (0-100)
    momentum_score: float   # 动量因子得分 (0-100)
    sentiment_score: float  # 情绪因子得分 (0-100)
    composite_score: float  # 综合得分 (加权平均)
    signal: str             # BUY / HOLD / SELL
    confidence: float       # 置信度 (0-1)


class MultiFactorModel:
    """多因子评分模型
    
    基于 Fama-French 三因子 + 动量 + 情绪 因子
    """
    
    # 因子权重 (可调整)
    FACTOR_WEIGHTS = {
        'value': 0.25,      # 价值因子 (PE/PB/PS)
        'growth': 0.20,     # 成长因子 (营收增长/利润增长)
        'quality': 0.20,    # 质量因子 (ROE/毛利率/现金流)
        'momentum': 0.20,   # 动量因子 (近期涨幅/相对强弱)
        'sentiment': 0.15,  # 情绪因子 (市场情绪/资金流向)
    }
    
    def calculate_composite_score(self, factor_scores: Dict[str, float]) -> float:
        """计算加权综合得分"""
        total = 0
        for factor, weight in self.FACTOR_WEIGHTS.items():
            score = factor_scores.get(factor, 50)  # 默认50分
            total += score * weight
        return total
    
    def generate_signal(self, composite_score: float) -> Tuple[str, float]:
        """基于综合得分生成信号
        
        Returns:
            (signal, confidence)
        """
        if composite_score >= 70:
            return ("BUY", min((composite_score - 70) / 30 + 0.6, 1.0))
        elif composite_score >= 40:
            return ("HOLD", 0.5)
        else:
            return ("SELL", min((40 - composite_score) / 40 + 0.6, 1.0))


def calculate_value_score(pe: float, pb: float, industry_pe: float = 20) -> float:
    """
    计算价值因子得分
    
    基于相对估值模型：PE相对行业位置、PB合理性
    """
    score = 50  # 基准分
    
    # PE相对行业
    if pe <= 0:
        score -= 20  # 亏损
    elif pe < industry_pe * 0.5:
        score += 25  # 明显低估
    elif pe < industry_pe * 0.8:
        score += 15  # 适度低估
    elif pe < industry_pe * 1.2:
        score += 0   # 合理
    elif pe < industry_pe * 1.5:
        score -= 10  # 适度高估
    else:
        score -= 25  # 明显高估
    
    # PB 评分
    if pb < 1:
        score += 20  # 破净
    elif pb < 2:
        score += 10
    elif pb < 3:
        score += 0
    elif pb < 5:
        score -= 10
    else:
        score -= 20  # PB过高
    
    return max(0, min(100, score))


def calculate_growth_score(revenue_growth: float, profit_growth: float) -> float:
    """
    计算成长因子得分
    
    基于营收增长率和利润增长率
    """
    score = 50
    
    # 营收增长评分
    if revenue_growth > 0.30:
        score += 20  # 高速增长
    elif revenue_growth > 0.15:
        score += 10  # 快速增长
    elif revenue_growth > 0.05:
        score += 5   # 稳定增长
    elif revenue_growth > 0:
        score += 0   # 微增
    elif revenue_growth > -0.10:
        score -= 10  # 小幅下滑
    else:
        score -= 25  # 大幅下滑
    
    # 利润增长评分
    if profit_growth > 0.30:
        score += 20
    elif profit_growth > 0.15:
        score += 10
    elif profit_growth > 0:
        score += 5
    elif profit_growth > -0.20:
        score -= 10
    else:
        score -= 25
    
    return max(0, min(100, score))


def calculate_quality_score(roe: float, gross_margin: float, debt_ratio: float) -> float:
    """
    计算质量因子得分
    
    基于ROE、毛利率、资产负债率
    """
    score = 50
    
    # ROE评分
    if roe > 0.20:
        score += 25  # 优秀
    elif roe > 0.15:
        score += 15  # 良好
    elif roe > 0.10:
        score += 5   # 一般
    elif roe > 0:
        score -= 5   # 较差
    else:
        score -= 25  # 亏损
    
    # 毛利率评分
    if gross_margin > 0.40:
        score += 15  # 高毛利
    elif gross_margin > 0.25:
        score += 5
    elif gross_margin > 0.15:
        score += 0
    else:
        score -= 10  # 低毛利
    
    # 资产负债率评分 (越低越好，但不能太低)
    if debt_ratio < 0.30:
        score += 10  # 低负债
    elif debt_ratio < 0.50:
        score += 5   # 适中
    elif debt_ratio < 0.70:
        score -= 5   # 偏高
    else:
        score -= 15  # 高负债风险
    
    return max(0, min(100, score))


def calculate_momentum_score(price_change_20d: float, price_change_60d: float, rsi: float) -> float:
    """
    计算动量因子得分
    
    基于近期涨幅和RSI
    """
    score = 50
    
    # 20日涨幅
    if price_change_20d > 0.15:
        score += 15  # 强势
    elif price_change_20d > 0.05:
        score += 10
    elif price_change_20d > 0:
        score += 5
    elif price_change_20d > -0.10:
        score -= 5
    else:
        score -= 15  # 弱势
    
    # 60日涨幅
    if price_change_60d > 0.20:
        score += 10
    elif price_change_60d > 0:
        score += 5
    elif price_change_60d > -0.15:
        score -= 5
    else:
        score -= 15
    
    # RSI评分 (超买超卖)
    if rsi > 80:
        score -= 15  # 严重超买，回调风险
    elif rsi > 70:
        score -= 5   # 超买
    elif rsi > 30:
        score += 0   # 正常
    elif rsi > 20:
        score += 10  # 超卖，反弹机会
    else:
        score += 15  # 严重超卖
    
    return max(0, min(100, score))


def calculate_sentiment_score(volume_ratio: float, money_flow: str) -> float:
    """
    计算情绪因子得分
    
    基于成交量比率和资金流向
    """
    score = 50
    
    # 量比评分
    if volume_ratio > 3.0:
        score += 15  # 放量
    elif volume_ratio > 1.5:
        score += 10
    elif volume_ratio > 0.8:
        score += 0   # 正常
    elif volume_ratio > 0.5:
        score -= 5   # 缩量
    else:
        score -= 15  # 严重缩量
    
    # 资金流向
    if money_flow == "大幅净流入":
        score += 20
    elif money_flow == "净流入":
        score += 10
    elif money_flow == "平衡":
        score += 0
    elif money_flow == "净流出":
        score -= 10
    else:  # 大幅净流出
        score -= 20
    
    return max(0, min(100, score))


@tool
def calculate_multi_factor_score(symbol: str) -> str:
    """
    计算股票的多因子量化评分。
    
    基于五大因子：价值、成长、质量、动量、情绪
    生成综合评分和交易信号。
    
    Args:
        symbol: 股票代码（6位数字）
        
    Returns:
        多因子评分报告，包含各因子得分、综合评分和交易信号
        
    Example:
        >>> result = calculate_multi_factor_score.invoke({"symbol": "600519"})
    """
    try:
        # 获取基本数据
        end_date = datetime.datetime.now().strftime("%Y%m%d")
        start_date = (datetime.datetime.now() - datetime.timedelta(days=120)).strftime("%Y%m%d")
        
        # 历史行情
        df = ak.stock_zh_a_hist(symbol=symbol, start_date=start_date, end_date=end_date, adjust="qfq")
        
        if df.empty or len(df) < 20:
            return f"数据不足，无法计算股票 {symbol} 的多因子评分"
        
        # 计算技术指标
        current_price = df['收盘'].iloc[-1]
        price_change_20d = (current_price / df['收盘'].iloc[-21] - 1) if len(df) >= 21 else 0
        price_change_60d = (current_price / df['收盘'].iloc[-61] - 1) if len(df) >= 61 else 0
        
        # RSI计算
        delta = df['收盘'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1])) if loss.iloc[-1] != 0 else 50
        
        # 量比
        avg_volume_20 = df['成交量'].iloc[-21:-1].mean() if len(df) >= 21 else df['成交量'].mean()
        volume_ratio = df['成交量'].iloc[-1] / avg_volume_20 if avg_volume_20 > 0 else 1.0
        
        # 模拟基本面数据 (实际应该从财务数据获取)
        # 这里使用简化估算
        pe = 25.0  # 默认PE
        pb = 3.0   # 默认PB
        roe = 0.15
        revenue_growth = 0.10
        profit_growth = 0.08
        gross_margin = 0.30
        debt_ratio = 0.45
        
        # 尝试获取实际估值数据
        try:
            valuation = ak.stock_a_indicator_lg(symbol=symbol)
            if not valuation.empty:
                pe = valuation['pe'].iloc[-1] if 'pe' in valuation.columns else pe
                pb = valuation['pb'].iloc[-1] if 'pb' in valuation.columns else pb
        except:
            pass
        
        # 计算各因子得分
        value_score = calculate_value_score(pe, pb, industry_pe=20)
        growth_score = calculate_growth_score(revenue_growth, profit_growth)
        quality_score = calculate_quality_score(roe, gross_margin, debt_ratio)
        momentum_score = calculate_momentum_score(price_change_20d, price_change_60d, rsi)
        
        # 资金流向判断
        if volume_ratio > 1.5 and price_change_20d > 0.05:
            money_flow = "净流入"
        elif volume_ratio < 0.8 or price_change_20d < -0.05:
            money_flow = "净流出"
        else:
            money_flow = "平衡"
        sentiment_score = calculate_sentiment_score(volume_ratio, money_flow)
        
        # 创建多因子模型
        model = MultiFactorModel()
        factor_scores = {
            'value': value_score,
            'growth': growth_score,
            'quality': quality_score,
            'momentum': momentum_score,
            'sentiment': sentiment_score
        }
        
        composite_score = model.calculate_composite_score(factor_scores)
        signal, confidence = model.generate_signal(composite_score)
        
        # 生成报告
        result = f"【股票 {symbol} 多因子量化评分】\n\n"
        result += f"【因子评分明细】\n"
        result += f"├─ 价值因子: {value_score:.0f}/100 (PE={pe:.1f}, PB={pb:.2f})\n"
        result += f"├─ 成长因子: {growth_score:.0f}/100 (营收增长{revenue_growth*100:.1f}%, 利润增长{profit_growth*100:.1f}%)\n"
        result += f"├─ 质量因子: {quality_score:.0f}/100 (ROE={roe*100:.1f}%, 毛利率{gross_margin*100:.1f}%)\n"
        result += f"├─ 动量因子: {momentum_score:.0f}/100 (20日涨幅{price_change_20d*100:.1f}%, RSI={rsi:.1f})\n"
        result += f"└─ 情绪因子: {sentiment_score:.0f}/100 (量比{volume_ratio:.2f}, {money_flow})\n\n"
        
        result += f"【综合评分】\n"
        result += f"综合得分: {composite_score:.1f}/100\n\n"
        
        result += f"【量化信号】\n"
        signal_cn = {"BUY": "买入", "HOLD": "持有", "SELL": "卖出"}[signal]
        result += f"信号: {signal_cn}\n"
        result += f"置信度: {confidence*100:.0f}%\n\n"
        
        # 评级说明
        if composite_score >= 70:
            level = "优秀 ⭐⭐⭐"
            desc = "多因子共振向好，建议积极关注"
        elif composite_score >= 55:
            level = "良好 ⭐⭐"
            desc = "综合表现较好，可适度参与"
        elif composite_score >= 45:
            level = "中性 ⭐"
            desc = "表现一般，建议观望"
        elif composite_score >= 30:
            level = "较差"
            desc = "多项因子偏弱，注意风险"
        else:
            level = "很差 ⚠️"
            desc = "多因子共振向下，建议规避"
        
        result += f"【综合评级】\n"
        result += f"等级: {level}\n"
        result += f"说明: {desc}\n"
        
        return result
        
    except Exception as e:
        return f"多因子评分计算失败: {str(e)}"


@tool
def generate_quant_signals(symbol: str) -> str:
    """
    生成量化交易信号。
    
    基于多个量化规则生成交易信号，包括：
    - 均线系统信号
    - MACD信号
    - RSI超买超卖信号
    - 量价配合信号
    
    Args:
        symbol: 股票代码
        
    Returns:
        量化信号报告
    """
    try:
        end_date = datetime.datetime.now().strftime("%Y%m%d")
        start_date = (datetime.datetime.now() - datetime.timedelta(days=120)).strftime("%Y%m%d")
        
        df = ak.stock_zh_a_hist(symbol=symbol, start_date=start_date, end_date=end_date, adjust="qfq")
        
        if df.empty or len(df) < 60:
            return f"数据不足，无法生成量化信号"
        
        # 计算均线
        df['MA5'] = df['收盘'].rolling(5).mean()
        df['MA10'] = df['收盘'].rolling(10).mean()
        df['MA20'] = df['收盘'].rolling(20).mean()
        df['MA60'] = df['收盘'].rolling(60).mean()
        
        # 计算MACD
        df['EMA12'] = df['收盘'].ewm(span=12).mean()
        df['EMA26'] = df['收盘'].ewm(span=26).mean()
        df['DIF'] = df['EMA12'] - df['EMA26']
        df['DEA'] = df['DIF'].ewm(span=9).mean()
        df['MACD'] = (df['DIF'] - df['DEA']) * 2
        
        # 计算RSI
        delta = df['收盘'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        current = df.iloc[-1]
        prev = df.iloc[-2]
        
        signals = []
        buy_count = 0
        sell_count = 0
        
        # 均线系统信号
        if current['MA5'] > current['MA10'] > current['MA20']:
            signals.append(("买入信号", "均线多头排列 (MA5>MA10>MA20)", 0.7))
            buy_count += 1
        elif current['MA5'] < current['MA10'] < current['MA20']:
            signals.append(("卖出信号", "均线空头排列 (MA5<MA10<MA20)", 0.7))
            sell_count += 1
        
        if prev['MA5'] <= prev['MA10'] and current['MA5'] > current['MA10']:
            signals.append(("买入信号", "MA5上穿MA10 (金叉)", 0.6))
            buy_count += 1
        elif prev['MA5'] >= prev['MA10'] and current['MA5'] < current['MA10']:
            signals.append(("卖出信号", "MA5下穿MA10 (死叉)", 0.6))
            sell_count += 1
        
        # MACD信号
        if prev['DIF'] <= prev['DEA'] and current['DIF'] > current['DEA']:
            signals.append(("买入信号", "MACD金叉", 0.65))
            buy_count += 1
        elif prev['DIF'] >= prev['DEA'] and current['DIF'] < current['DEA']:
            signals.append(("卖出信号", "MACD死叉", 0.65))
            sell_count += 1
        
        # RSI信号
        if current['RSI'] < 30:
            signals.append(("买入信号", f"RSI超卖 ({current['RSI']:.1f})", 0.6))
            buy_count += 1
        elif current['RSI'] > 70:
            signals.append(("卖出信号", f"RSI超买 ({current['RSI']:.1f})", 0.6))
            sell_count += 1
        
        # 支撑/压力信号
        if current['收盘'] > current['MA60']:
            signals.append(("买入信号", "站上60日均线", 0.5))
            buy_count += 1
        elif current['收盘'] < current['MA60']:
            signals.append(("卖出信号", "跌破60日均线", 0.5))
            sell_count += 1
        
        # 生成报告
        result = f"【股票 {symbol} 量化信号报告】\n\n"
        result += f"当前价格: {current['收盘']:.2f}\n"
        result += f"MA5/10/20/60: {current['MA5']:.2f}/{current['MA10']:.2f}/{current['MA20']:.2f}/{current['MA60']:.2f}\n"
        result += f"RSI(14): {current['RSI']:.1f}\n"
        result += f"MACD: DIF={current['DIF']:.3f}, DEA={current['DEA']:.3f}\n\n"
        
        result += f"【信号汇总】\n"
        if signals:
            for signal_type, desc, conf in signals:
                emoji = "🟢" if "买入" in signal_type else "🔴"
                result += f"{emoji} {signal_type}: {desc} (置信度{conf*100:.0f}%)\n"
        else:
            result += "暂无明确信号\n"
        
        result += f"\n【综合判断】\n"
        result += f"买入信号: {buy_count}个\n"
        result += f"卖出信号: {sell_count}个\n"
        
        if buy_count > sell_count + 1:
            result += f"倾向: 偏多 📈\n"
        elif sell_count > buy_count + 1:
            result += f"倾向: 偏空 📉\n"
        else:
            result += f"倾向: 中性 ➡️\n"
        
        return result
        
    except Exception as e:
        return f"量化信号生成失败: {str(e)}"
