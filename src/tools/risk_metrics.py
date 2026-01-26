"""
Risk Metrics Tools
风险度量工具集

提供专业的风险分析指标：
- 波动率计算
- 贝塔系数
- 最大回撤
- 夏普比率
- VaR (风险价值)
"""

import akshare as ak
import pandas as pd
import numpy as np
from langchain_core.tools import tool
from typing import Optional
import datetime


@tool
def calculate_volatility(symbol: str, period: int = 60) -> str:
    """
    计算股票的历史波动率。
    
    波动率是衡量股票价格波动程度的重要指标。
    年化波动率 = 日波动率 × √252
    
    Args:
        symbol: 股票代码（6位数字）
        period: 计算周期（天数），默认60天
        
    Returns:
        波动率分析报告
        
    Example:
        >>> result = calculate_volatility.invoke({"symbol": "600519", "period": 60})
    """
    try:
        # 获取历史数据
        end_date = datetime.datetime.now().strftime("%Y%m%d")
        start_date = (datetime.datetime.now() - datetime.timedelta(days=period + 30)).strftime("%Y%m%d")
        
        df = ak.stock_zh_a_hist(symbol=symbol, start_date=start_date, end_date=end_date, adjust="qfq")
        
        if df.empty or len(df) < 20:
            return f"数据不足，无法计算股票 {symbol} 的波动率"
        
        # 计算日收益率
        df['returns'] = df['收盘'].pct_change()
        
        # 计算波动率
        daily_vol = df['returns'].std()
        annual_vol = daily_vol * np.sqrt(252)  # 年化
        
        # 计算波动率的历史分位数
        rolling_vol = df['returns'].rolling(20).std() * np.sqrt(252)
        current_vol_percentile = (rolling_vol.iloc[-1] < rolling_vol).mean() * 100
        
        result = f"【股票 {symbol} 波动率分析】\n\n"
        result += f"【历史波动率】\n"
        result += f"日波动率: {daily_vol*100:.2f}%\n"
        result += f"年化波动率: {annual_vol*100:.2f}%\n"
        result += f"波动率分位数: {current_vol_percentile:.1f}%\n\n"
        
        # 波动率评级
        if annual_vol < 0.20:
            vol_level = "低波动 ✓"
            risk_desc = "股价波动较小，风险相对可控"
        elif annual_vol < 0.35:
            vol_level = "中等波动"
            risk_desc = "波动处于正常水平"
        elif annual_vol < 0.50:
            vol_level = "高波动 ⚠️"
            risk_desc = "波动较大，需注意风险控制"
        else:
            vol_level = "极高波动 🚨"
            risk_desc = "波动极大，高风险品种"
        
        result += f"【波动率评级】\n"
        result += f"等级: {vol_level}\n"
        result += f"说明: {risk_desc}\n\n"
        
        # 近期走势
        result += f"【近期走势】\n"
        result += f"近5日涨幅: {(df['收盘'].iloc[-1]/df['收盘'].iloc[-6]-1)*100:.2f}%\n"
        result += f"近20日涨幅: {(df['收盘'].iloc[-1]/df['收盘'].iloc[-21]-1)*100:.2f}%\n"
        
        return result
        
    except Exception as e:
        return f"波动率计算失败: {str(e)}"


@tool
def calculate_beta(symbol: str, benchmark: str = "000300", period: int = 120) -> str:
    """
    计算股票的贝塔系数。
    
    贝塔衡量个股相对于大盘的系统性风险：
    - Beta > 1: 波动大于市场，进攻型
    - Beta = 1: 波动与市场同步
    - Beta < 1: 波动小于市场，防守型
    
    Args:
        symbol: 股票代码（6位数字）
        benchmark: 基准指数代码，默认沪深300(000300)
        period: 计算周期（天数），默认120天
        
    Returns:
        贝塔系数分析报告
    """
    try:
        end_date = datetime.datetime.now().strftime("%Y%m%d")
        start_date = (datetime.datetime.now() - datetime.timedelta(days=period + 30)).strftime("%Y%m%d")
        
        # 获取个股数据
        stock_df = ak.stock_zh_a_hist(symbol=symbol, start_date=start_date, end_date=end_date, adjust="qfq")
        
        # 获取指数数据
        index_df = ak.stock_zh_index_daily(symbol=f"sh{benchmark}")
        index_df = index_df[index_df['date'] >= start_date]
        
        if stock_df.empty or index_df.empty:
            return f"数据不足，无法计算贝塔系数"
        
        # 计算收益率
        stock_returns = stock_df['收盘'].pct_change().dropna()
        index_returns = index_df['close'].pct_change().dropna()
        
        # 对齐数据
        min_len = min(len(stock_returns), len(index_returns))
        stock_returns = stock_returns.tail(min_len).values
        index_returns = index_returns.tail(min_len).values
        
        # 计算贝塔
        covariance = np.cov(stock_returns, index_returns)[0][1]
        variance = np.var(index_returns)
        beta = covariance / variance if variance != 0 else 1.0
        
        # 计算相关系数
        correlation = np.corrcoef(stock_returns, index_returns)[0][1]
        
        result = f"【股票 {symbol} 贝塔系数分析】\n\n"
        result += f"【贝塔系数】\n"
        result += f"Beta: {beta:.2f}\n"
        result += f"与大盘相关性: {correlation:.2f}\n\n"
        
        # 贝塔评级
        if beta > 1.5:
            beta_type = "高贝塔 (进攻型) 🚀"
            risk_desc = "波动显著大于市场，适合牛市"
        elif beta > 1.0:
            beta_type = "中高贝塔"
            risk_desc = "波动略大于市场"
        elif beta > 0.7:
            beta_type = "中等贝塔"
            risk_desc = "波动与市场接近"
        elif beta > 0.3:
            beta_type = "低贝塔 (防守型) 🛡️"
            risk_desc = "波动小于市场，适合熊市防守"
        else:
            beta_type = "极低贝塔"
            risk_desc = "与市场相关性很低"
        
        result += f"【贝塔评级】\n"
        result += f"类型: {beta_type}\n"
        result += f"说明: {risk_desc}\n"
        
        return result
        
    except Exception as e:
        return f"贝塔系数计算失败: {str(e)}"


@tool
def calculate_max_drawdown(symbol: str, period: int = 252) -> str:
    """
    计算股票的最大回撤。
    
    最大回撤是从最高点到最低点的最大跌幅，是衡量风险的重要指标。
    
    Args:
        symbol: 股票代码（6位数字）
        period: 计算周期（天数），默认252天（约一年）
        
    Returns:
        最大回撤分析报告
    """
    try:
        end_date = datetime.datetime.now().strftime("%Y%m%d")
        start_date = (datetime.datetime.now() - datetime.timedelta(days=period + 30)).strftime("%Y%m%d")
        
        df = ak.stock_zh_a_hist(symbol=symbol, start_date=start_date, end_date=end_date, adjust="qfq")
        
        if df.empty or len(df) < 20:
            return f"数据不足，无法计算最大回撤"
        
        prices = df['收盘'].values
        
        # 计算累计最大值
        cummax = np.maximum.accumulate(prices)
        
        # 计算回撤
        drawdown = (cummax - prices) / cummax
        max_drawdown = np.max(drawdown)
        
        # 找到最大回撤的起止点
        end_idx = np.argmax(drawdown)
        start_idx = np.argmax(prices[:end_idx+1]) if end_idx > 0 else 0
        
        result = f"【股票 {symbol} 最大回撤分析】\n\n"
        result += f"【最大回撤】\n"
        result += f"最大回撤幅度: {max_drawdown*100:.2f}%\n"
        result += f"最高点: {prices[start_idx]:.2f}元\n"
        result += f"最低点: {prices[end_idx]:.2f}元\n"
        result += f"回撤持续天数: {end_idx - start_idx}天\n\n"
        
        # 回撤评级
        if max_drawdown < 0.15:
            dd_level = "小幅回撤 ✓"
            risk_desc = "回撤较小，风险控制良好"
        elif max_drawdown < 0.30:
            dd_level = "中等回撤"
            risk_desc = "回撤处于正常范围"
        elif max_drawdown < 0.50:
            dd_level = "大幅回撤 ⚠️"
            risk_desc = "经历过较大回撤，需注意风险"
        else:
            dd_level = "巨幅回撤 🚨"
            risk_desc = "回撤超过50%，风险极高"
        
        result += f"【回撤评级】\n"
        result += f"等级: {dd_level}\n"
        result += f"说明: {risk_desc}\n"
        
        return result
        
    except Exception as e:
        return f"最大回撤计算失败: {str(e)}"


@tool
def calculate_sharpe_ratio(symbol: str, risk_free_rate: float = 0.02, period: int = 252) -> str:
    """
    计算股票的夏普比率。
    
    夏普比率 = (收益率 - 无风险利率) / 波动率
    衡量每承担一单位风险能获得多少超额收益。
    
    Args:
        symbol: 股票代码
        risk_free_rate: 无风险利率，默认2%
        period: 计算周期，默认252天
        
    Returns:
        夏普比率分析报告
    """
    try:
        end_date = datetime.datetime.now().strftime("%Y%m%d")
        start_date = (datetime.datetime.now() - datetime.timedelta(days=period + 30)).strftime("%Y%m%d")
        
        df = ak.stock_zh_a_hist(symbol=symbol, start_date=start_date, end_date=end_date, adjust="qfq")
        
        if df.empty or len(df) < 60:
            return f"数据不足，无法计算夏普比率"
        
        # 计算收益率
        returns = df['收盘'].pct_change().dropna()
        
        # 年化收益率
        annual_return = (1 + returns.mean()) ** 252 - 1
        
        # 年化波动率
        annual_vol = returns.std() * np.sqrt(252)
        
        # 夏普比率
        sharpe = (annual_return - risk_free_rate) / annual_vol if annual_vol != 0 else 0
        
        result = f"【股票 {symbol} 夏普比率分析】\n\n"
        result += f"【风险调整收益】\n"
        result += f"年化收益率: {annual_return*100:.2f}%\n"
        result += f"年化波动率: {annual_vol*100:.2f}%\n"
        result += f"无风险利率: {risk_free_rate*100:.2f}%\n"
        result += f"夏普比率: {sharpe:.2f}\n\n"
        
        # 夏普评级
        if sharpe > 2.0:
            sharpe_level = "优秀 ⭐⭐⭐"
            desc = "风险调整后收益非常出色"
        elif sharpe > 1.0:
            sharpe_level = "良好 ⭐⭐"
            desc = "风险调整后收益较好"
        elif sharpe > 0.5:
            sharpe_level = "一般 ⭐"
            desc = "风险调整后收益一般"
        elif sharpe > 0:
            sharpe_level = "较差"
            desc = "收益未能很好补偿风险"
        else:
            sharpe_level = "负收益 ⚠️"
            desc = "收益为负，不如持有现金"
        
        result += f"【夏普评级】\n"
        result += f"等级: {sharpe_level}\n"
        result += f"说明: {desc}\n"
        
        return result
        
    except Exception as e:
        return f"夏普比率计算失败: {str(e)}"


@tool
def calculate_var(symbol: str, confidence: float = 0.95, period: int = 60) -> str:
    """
    计算风险价值(VaR)。
    
    VaR表示在给定置信水平下，一定时期内的最大可能损失。
    
    Args:
        symbol: 股票代码
        confidence: 置信水平，默认95%
        period: 历史数据周期，默认60天
        
    Returns:
        VaR分析报告
    """
    try:
        end_date = datetime.datetime.now().strftime("%Y%m%d")
        start_date = (datetime.datetime.now() - datetime.timedelta(days=period + 30)).strftime("%Y%m%d")
        
        df = ak.stock_zh_a_hist(symbol=symbol, start_date=start_date, end_date=end_date, adjust="qfq")
        
        if df.empty or len(df) < 30:
            return f"数据不足，无法计算VaR"
        
        # 计算日收益率
        returns = df['收盘'].pct_change().dropna()
        
        # 历史VaR (直接用历史分位数)
        var_95 = np.percentile(returns, (1 - confidence) * 100)
        var_99 = np.percentile(returns, 1)
        
        # 参数VaR (假设正态分布)
        import scipy.stats as stats
        mean = returns.mean()
        std = returns.std()
        param_var_95 = mean - std * stats.norm.ppf(confidence)
        
        # 当前价格
        current_price = df['收盘'].iloc[-1]
        
        result = f"【股票 {symbol} 风险价值(VaR)分析】\n\n"
        result += f"当前价格: {current_price:.2f}元\n\n"
        result += f"【每日VaR (历史模拟法)】\n"
        result += f"95%置信度VaR: {abs(var_95)*100:.2f}%\n"
        result += f"  - 意味着有95%的把握，单日亏损不超过{abs(var_95)*100:.2f}%\n"
        result += f"  - 约等于: {current_price * abs(var_95):.2f}元/股\n\n"
        result += f"99%置信度VaR: {abs(var_99)*100:.2f}%\n"
        result += f"  - 意味着有99%的把握，单日亏损不超过{abs(var_99)*100:.2f}%\n\n"
        
        result += f"【风险提示】\n"
        if abs(var_95) > 0.05:
            result += f"⚠️ 日VaR较高，单日可能出现较大波动\n"
        else:
            result += f"✓ 日VaR处于正常水平\n"
        
        return result
        
    except Exception as e:
        return f"VaR计算失败: {str(e)}"
