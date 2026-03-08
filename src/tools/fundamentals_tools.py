"""
Fundamentals Analysis Tools
基本面分析工具集

专为Fundamentals Analyst设计的工具集，提供：
- 公司财务数据分析
- 内在价值计算
- 业绩指标评估
- 财务风险识别
"""

import akshare as ak
import pandas as pd
from langchain_core.tools import tool
from typing import Optional
import datetime


@tool
def get_company_financials(symbol: str) -> str:
    """
    获取公司的财务报表数据。
    
    包括资产负债表、利润表、现金流量表的关键指标。
    
    Args:
        symbol: 股票代码（6位数字）
        
    Returns:
        公司财务数据摘要
        
    Example:
        >>> result = get_company_financials.invoke({"symbol": "600519"})
    """
    try:
        result = f"【股票 {symbol} 公司财务数据】\n\n"
        
        # 获取股票基本信息
        try:
            stock_info = ak.stock_individual_info_em(symbol=symbol)
            
            if not stock_info.empty:
                result += "【基本信息】\n"
                for idx, row in stock_info.iterrows():
                    item = row['item']
                    value = row['value']
                    if item in ['总市值', '流通市值', '总股本', '流通股']:
                        result += f"  {item}: {value}\n"
                result += "\n"
        except:
            result += "【基本信息】 获取失败\n\n"
        
        # 获取主要财务指标
        try:
            # 使用财务指标接口
            financial_df = ak.stock_financial_analysis_indicator(symbol=symbol)
            
            if not financial_df.empty:
                latest = financial_df.iloc[0]  # 最新一期
                
                result += f"【主要财务指标】 (报告期: {latest.get('报告期', 'N/A')})\n\n"
                
                # 盈利能力
                result += "盈利能力:\n"
                result += f"  净资产收益率(ROE): {latest.get('净资产收益率', 'N/A')}%\n"
                result += f"  总资产收益率(ROA): {latest.get('总资产净利率', 'N/A')}%\n"
                result += f"  销售净利率: {latest.get('销售净利率', 'N/A')}%\n"
                result += f"  毛利率: {latest.get('销售毛利率', 'N/A')}%\n\n"
                
                # 成长能力
                result += "成长能力:\n"
                result += f"  营业收入同比增长: {latest.get('营业收入同比增长', 'N/A')}%\n"
                result += f"  净利润同比增长: {latest.get('净利润同比增长', 'N/A')}%\n\n"
                
                # 偿债能力
                result += "偿债能力:\n"
                result += f"  资产负债率: {latest.get('资产负债率', 'N/A')}%\n"
                result += f"  流动比率: {latest.get('流动比率', 'N/A')}\n"
                result += f"  速动比率: {latest.get('速动比率', 'N/A')}\n\n"
                
                # 营运能力
                result += "营运能力:\n"
                result += f"  总资产周转率: {latest.get('总资产周转率', 'N/A')}\n"
                result += f"  应收账款周转率: {latest.get('应收账款周转率', 'N/A')}\n"
                
        except Exception as e:
            result += f"【主要财务指标】 获取失败: {str(e)}\n"
        
        return result
        
    except Exception as e:
        return f"公司财务数据获取失败: {str(e)}"


@tool
def calculate_intrinsic_value(symbol: str) -> str:
    """
    计算股票的内在价值评估。
    
    基于财务数据和估值模型，评估股票的合理价值区间。
    
    Args:
        symbol: 股票代码（6位数字）
        
    Returns:
        内在价值评估报告
        
    Example:
        >>> result = calculate_intrinsic_value.invoke({"symbol": "600519"})
    """
    try:
        result = f"【股票 {symbol} 内在价值评估】\n\n"
        
        # 获取当前股价
        try:
            realtime = ak.stock_zh_a_spot_em()
            stock_data = realtime[realtime['代码'] == symbol]
            
            if not stock_data.empty:
                current_price = float(stock_data.iloc[0]['最新价'])
                result += f"当前股价: {current_price:.2f}元\n\n"
            else:
                current_price = None
                result += "当前股价: 获取失败\n\n"
        except:
            current_price = None
            result += "当前股价: 获取失败\n\n"
        
        # 获取估值指标
        try:
            # 获取市盈率等估值数据
            stock_info = ak.stock_individual_info_em(symbol=symbol)
            
            pe_ratio = None
            pb_ratio = None
            
            for idx, row in stock_info.iterrows():
                if row['item'] == '市盈率-动态':
                    pe_ratio = float(row['value'])
                elif row['item'] == '市净率':
                    pb_ratio = float(row['value'])
            
            result += "【估值指标】\n"
            result += f"市盈率(PE): {pe_ratio if pe_ratio else 'N/A'}\n"
            result += f"市净率(PB): {pb_ratio if pb_ratio else 'N/A'}\n\n"
            
            # 行业平均估值对比
            result += "【估值分析】\n"
            
            if pe_ratio:
                if pe_ratio < 15:
                    pe_assessment = "低估 (PE较低)"
                elif pe_ratio < 30:
                    pe_assessment = "合理 (PE适中)"
                elif pe_ratio < 50:
                    pe_assessment = "偏高 (PE较高)"
                else:
                    pe_assessment = "高估 (PE很高)"
                
                result += f"PE评估: {pe_assessment}\n"
            
            if pb_ratio:
                if pb_ratio < 1:
                    pb_assessment = "破净 (PB<1，可能低估)"
                elif pb_ratio < 3:
                    pb_assessment = "合理 (PB适中)"
                elif pb_ratio < 5:
                    pb_assessment = "偏高 (PB较高)"
                else:
                    pb_assessment = "高估 (PB很高)"
                
                result += f"PB评估: {pb_assessment}\n"
            
            result += "\n"
            
            # 简化的内在价值估算
            if current_price and pe_ratio:
                # 使用行业平均PE倒推合理价值
                industry_avg_pe = 20  # 假设行业平均PE为20
                
                eps = current_price / pe_ratio if pe_ratio > 0 else 0
                fair_value = eps * industry_avg_pe
                
                result += "【内在价值估算】\n"
                result += f"基于行业平均PE估算:\n"
                result += f"  合理价值: {fair_value:.2f}元\n"
                result += f"  当前价格: {current_price:.2f}元\n"
                
                discount = ((fair_value - current_price) / fair_value * 100) if fair_value > 0 else 0
                
                if discount > 20:
                    valuation = f"低估约{discount:.1f}% 💡"
                elif discount > -20:
                    valuation = "估值合理 ✓"
                else:
                    valuation = f"高估约{abs(discount):.1f}% ⚠️"
                
                result += f"  估值判断: {valuation}\n\n"
            
        except Exception as e:
            result += f"估值数据获取失败: {str(e)}\n"
        
        result += "【投资建议】\n"
        result += "内在价值评估仅供参考，实际投资需综合考虑：\n"
        result += "• 公司成长性\n"
        result += "• 行业前景\n"
        result += "• 市场情绪\n"
        result += "• 宏观经济环境\n"
        
        return result
        
    except Exception as e:
        return f"内在价值计算失败: {str(e)}"


@tool
def get_performance_metrics(symbol: str) -> str:
    """
    获取公司业绩指标。
    
    包括PE、ROE、营收增长等关键业绩指标。
    
    Args:
        symbol: 股票代码（6位数字）
        
    Returns:
        业绩指标报告
        
    Example:
        >>> result = get_performance_metrics.invoke({"symbol": "600519"})
    """
    try:
        result = f"【股票 {symbol} 业绩指标分析】\n\n"
        
        # 获取财务指标
        try:
            financial_df = ak.stock_financial_analysis_indicator(symbol=symbol)
            
            if not financial_df.empty:
                # 获取最近4个季度的数据
                recent = financial_df.head(4)
                
                result += "【关键业绩指标趋势】\n\n"
                
                # ROE趋势
                roe_list = recent['净资产收益率'].tolist()
                result += f"净资产收益率(ROE)趋势:\n"
                for i, (idx, row) in enumerate(recent.iterrows()):
                    result += f"  {row['报告期']}: {row['净资产收益率']}%\n"
                
                result += "\n"
                
                # 营收和利润增长
                result += f"营收和利润增长:\n"
                latest = recent.iloc[0]
                result += f"  营业收入同比: {latest.get('营业收入同比增长', 'N/A')}%\n"
                result += f"  净利润同比: {latest.get('净利润同比增长', 'N/A')}%\n"
                result += f"  扣非净利润同比: {latest.get('扣非净利润同比增长', 'N/A')}%\n\n"
                
                # 盈利质量
                result += f"盈利质量:\n"
                result += f"  销售毛利率: {latest.get('销售毛利率', 'N/A')}%\n"
                result += f"  销售净利率: {latest.get('销售净利率', 'N/A')}%\n"
                result += f"  加权净资产收益率: {latest.get('加权净资产收益率', 'N/A')}%\n\n"
                
                # 业绩评估
                result += "【业绩评估】\n"
                
                try:
                    roe = float(latest.get('净资产收益率', 0))
                    revenue_growth = float(latest.get('营业收入同比增长', 0))
                    profit_growth = float(latest.get('净利润同比增长', 0))
                    
                    score = 0
                    insights = []
                    
                    if roe > 15:
                        score += 2
                        insights.append("✓ ROE优秀 (>15%)")
                    elif roe > 10:
                        score += 1
                        insights.append("✓ ROE良好 (>10%)")
                    else:
                        insights.append("⚠️ ROE偏低")
                    
                    if revenue_growth > 20:
                        score += 2
                        insights.append("✓ 营收高增长 (>20%)")
                    elif revenue_growth > 0:
                        score += 1
                        insights.append("✓ 营收正增长")
                    else:
                        insights.append("⚠️ 营收负增长")
                    
                    if profit_growth > 20:
                        score += 2
                        insights.append("✓ 利润高增长 (>20%)")
                    elif profit_growth > 0:
                        score += 1
                        insights.append("✓ 利润正增长")
                    else:
                        insights.append("⚠️ 利润负增长")
                    
                    for insight in insights:
                        result += f"{insight}\n"
                    
                    result += f"\n综合评分: {score}/6分\n"
                    
                    if score >= 5:
                        result += "业绩评级: 优秀 ⭐⭐⭐\n"
                    elif score >= 3:
                        result += "业绩评级: 良好 ⭐⭐\n"
                    else:
                        result += "业绩评级: 一般 ⭐\n"
                
                except:
                    pass
                
        except Exception as e:
            result += f"财务指标获取失败: {str(e)}\n"
        
        return result
        
    except Exception as e:
        return f"业绩指标分析失败: {str(e)}"


@tool
def identify_red_flags(symbol: str) -> str:
    """
    识别公司财务风险信号。
    
    分析财务报表中的异常指标和潜在风险。
    
    Args:
        symbol: 股票代码（6位数字）
        
    Returns:
        财务风险识别报告
        
    Example:
        >>> result = identify_red_flags.invoke({"symbol": "600519"})
    """
    try:
        result = f"【股票 {symbol} 财务风险识别】\n\n"
        
        red_flags = []
        warnings = []
        
        # 获取财务指标
        try:
            financial_df = ak.stock_financial_analysis_indicator(symbol=symbol)
            
            if not financial_df.empty:
                latest = financial_df.iloc[0]
                
                # 检查资产负债率
                try:
                    debt_ratio = float(latest.get('资产负债率', 0))
                    if debt_ratio > 70:
                        red_flags.append(f"🚨 资产负债率过高: {debt_ratio}% (>70%，财务杠杆风险)")
                    elif debt_ratio > 60:
                        warnings.append(f"⚠️ 资产负债率较高: {debt_ratio}% (>60%，需关注)")
                except:
                    pass
                
                # 检查流动比率
                try:
                    current_ratio = float(latest.get('流动比率', 0))
                    if current_ratio < 1:
                        red_flags.append(f"🚨 流动比率过低: {current_ratio} (<1，短期偿债能力不足)")
                    elif current_ratio < 1.5:
                        warnings.append(f"⚠️ 流动比率偏低: {current_ratio} (<1.5)")
                except:
                    pass
                
                # 检查营收和利润增长的背离
                try:
                    revenue_growth = float(latest.get('营业收入同比增长', 0))
                    profit_growth = float(latest.get('净利润同比增长', 0))
                    
                    if revenue_growth > 0 and profit_growth < -20:
                        red_flags.append(f"🚨 营收增长但利润大幅下滑 (营收{revenue_growth:+.1f}% vs 利润{profit_growth:+.1f}%)")
                    elif abs(revenue_growth - profit_growth) > 30:
                        warnings.append(f"⚠️ 营收和利润增速背离较大 (营收{revenue_growth:+.1f}% vs 利润{profit_growth:+.1f}%)")
                except:
                    pass
                
                # 检查ROE下降
                try:
                    if len(financial_df) >= 4:
                        current_roe = float(financial_df.iloc[0].get('净资产收益率', 0))
                        prev_roe = float(financial_df.iloc[3].get('净资产收益率', 0))
                        
                        if current_roe < prev_roe * 0.7:
                            red_flags.append(f"🚨 ROE大幅下滑: {current_roe}% (较一年前下降超30%)")
                except:
                    pass
                
                # 检查毛利率
                try:
                    gross_margin = float(latest.get('销售毛利率', 0))
                    if gross_margin < 10:
                        warnings.append(f"⚠️ 毛利率较低: {gross_margin}% (<10%，盈利能力弱)")
                except:
                    pass
                
        except Exception as e:
            result += f"财务数据分析失败: {str(e)}\n\n"
        
        # 输出风险识别结果
        if red_flags:
            result += "【严重风险信号 🚨】\n"
            for flag in red_flags:
                result += f"{flag}\n"
            result += "\n"
        
        if warnings:
            result += "【警示信号 ⚠️】\n"
            for warning in warnings:
                result += f"{warning}\n"
            result += "\n"
        
        if not red_flags and not warnings:
            result += "【风险评估】\n"
            result += "✓ 未发现明显的财务风险信号\n"
            result += "✓ 主要财务指标处于健康区间\n\n"
        
        result += "【投资建议】\n"
        if red_flags:
            result += "⚠️ 存在严重财务风险，建议谨慎投资或规避\n"
        elif warnings:
            result += "⚠️ 存在一些警示信号，建议深入研究后再决策\n"
        else:
            result += "✓ 财务状况相对健康，可继续关注\n"
        
        result += "\n注: 财务风险识别仅基于公开数据，实际投资需进一步尽职调查。"
        
        return result
        
    except Exception as e:
        return f"财务风险识别失败: {str(e)}"
