#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Enhanced Multi-Agent Stock Analysis - Command Line Interface
增强版多Agent股票分析系统 - 命令行入口

使用新的4层agent架构进行全面分析
"""

import sys
import argparse
from src.agent.multi_agent_system_enhanced import EnhancedMultiAgentSystem
from src.config import get_settings


def print_welcome():
    """打印欢迎信息"""
    print("=" * 80)
    print("           🚀 增强版多Agent股票交易分析系统")
    print("=" * 80)
    print("\n系统架构 (4层):")
    print("  📊 第1层: 分析师团队")
    print("      1️⃣  基本面分析师 - 财务健康度、估值分析")
    print("      2️⃣  情绪分析师 - 社交媒体情绪、市场情绪")
    print("      3️⃣  新闻分析师 - 新闻事件、宏观经济 🆕")
    print("      4️⃣  技术分析师 - MACD、RSI、均线系统")
    print("\n  🗣️  第2层: 研究员团队")
    print("      📈 看涨研究员 - 发掘上涨潜力")
    print("      📉 看跌研究员 - 识别下跌风险")
    print("      ⚔️  辩论机制 - 评分差异大时触发")
    print("\n  💼 第3层: 交易员")
    print("      🎯 综合决策 - 买入/持有/卖出")
    print("      📊 仓位建议 - 轻仓/半仓/重仓")
    print("\n  ⚖️  第4层: 风险评估与最终决策")
    print("      🔥 激进派风险评估")
    print("      ⚖️  中立派风险评估")
    print("      🛡️  保守派风险评估")
    print("      👔 投资组合经理 - 最终决策")
    print("\n特色功能:")
    print("  ✨ 4个专业分析师并行分析")
    print("  🆕 新闻分析师: 情感分析+宏观经济+事件影响")
    print("  🗣️  智能辩论: 多空分歧触发深度辩论")
    print("  🎯 分层决策: 4层架构确保全面性")
    print("  📊 3种风险视角: 适应不同投资风格")
    print("\n输入 'q' 或 'quit' 退出程序")
    print("=" * 80 + "\n")


def print_result(result):
    """格式化打印增强版分析结果"""
    print("\n" + "=" * 80)
    print("📊 增强版分析报告")
    print("=" * 80)
    
    print(f"\n股票代码: {result.symbol}")
    print(f"分析时间: {result.timestamp}")
    
    # ========== 分析师团队摘要 ==========
    print(f"\n{'='*80}")
    print("📊 第1层: 分析师团队评分")
    print(f"{'='*80}")
    print(f"基本面评分: {result.analyst_team.fundamentals.score}/10")
    print(f"技术面评分: {result.analyst_team.technical.score}/10")
    
    # ========== 研究员辩论 ==========
    print(f"\n{'='*80}")
    print("🗣️ 第2层: 研究员辩论")
    print(f"{'='*80}")
    print(f"多头评分: {result.researcher_debate.bullish.score}/10")
    print(f"空头评分: {result.researcher_debate.bearish.score}/10")
    print(f"评分差异: {result.researcher_debate.score_diff:.1f}")
    print(f"辩论状态: {'已触发辩论' if result.researcher_debate.debate_occurred else '未触发辩论'}")
    
    # ========== 交易员决策 ==========
    print(f"\n{'='*80}")
    print("💼 第3层: 交易员决策")
    print(f"{'='*80}")
    print(f"交易建议: {result.trader_decision.recommendation}")
    print(f"建议仓位: {result.trader_decision.suggested_position}")
    
    # ========== 最终决策 ==========
    print(f"\n{'='*80}")
    print("⚖️  第4层: 最终决策")
    print(f"{'='*80}")
    print(f"最终建议: {result.final_decision.recommendation}")
    print(f"信心水平: {result.final_decision.confidence}")
    print(f"\n仓位建议(按风险偏好):")
    for risk_type, position in result.final_decision.position_suggestions.items():
        print(f"  {risk_type}: {position}")
    
    # ========== 详细内容(可展开) ==========
    show_details = input("\n是否查看详细分析内容? (y/n): ").strip().lower()
    
    if show_details == 'y':
        print(f"\n{'='*80}")
        print("📋 第1层详细内容: 分析师团队")
        print(f"{'='*80}")
        
        print(f"\n【基本面分析师】")
        print(result.analyst_team.fundamentals.content)
        
        print(f"\n【情绪分析师】")
        print(result.analyst_team.sentiment.content)
        
        print(f"\n【新闻分析师】🆕")
        print(result.analyst_team.news.content)
        
        print(f"\n【技术分析师】")
        print(result.analyst_team.technical.content)
        
        print(f"\n{'='*80}")
        print("📋 第2层详细内容: 研究员辩论")
        print(f"{'='*80}")
        
        print(f"\n【多头观点】")
        print(result.researcher_debate.bullish.content)
        
        print(f"\n【空头观点】")
        print(result.researcher_debate.bearish.content)
        
        print(f"\n{'='*80}")
        print("📋 第3层详细内容: 交易员决策")
        print(f"{'='*80}")
        print(result.trader_decision.decision.content)
        
        print(f"\n{'='*80}")
        print("📋 第4层详细内容: 风险评估")
        print(f"{'='*80}")
        
        print(f"\n【激进派】")
        print(result.risk_assessment.aggressive.content)
        
        print(f"\n【中立派】")
        print(result.risk_assessment.neutral.content)
        
        print(f"\n【保守派】")
        print(result.risk_assessment.conservative.content)
        
        print(f"\n{'='*80}")
        print("📋 投资组合经理最终决策")
        print(f"{'='*80}")
        print(result.final_decision.decision.content)
    
    print("\n" + "=" * 80)
    print(f"✅ 分析完成!")
    print("=" * 80 + "\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='增强版多Agent股票交易分析系统')
    parser.add_argument('--symbol', '-s', type=str, help='股票代码')
    parser.add_argument('--threshold', '-t', type=float, default=3.0,
                       help='辩论触发阈值 (默认: 3.0)')
    parser.add_argument('--max-rounds', '-r', type=int, default=2,
                       help='最大辩论轮次 (默认: 2)')
    parser.add_argument('--no-verbose', action='store_true',
                       help='不显示详细过程')
    
    args = parser.parse_args()
    
    # 打印欢迎信息
    print_welcome()
    
    try:
        # 使用硅基流动API (测试阶段)
        api_key = "sk-glrkmcbkaybtvlnnvmvcakrchncpwadpxeibzitkpkgepueh"
        base_url = "https://api.siliconflow.cn/v1"
        
        # 初始化增强版多Agent系统
        print("🔧 正在初始化增强版多Agent系统...")
        print(f"   模型: Qwen/Qwen2.5-7B-Instruct")
        print(f"   辩论阈值: {args.threshold}")
        print(f"   最大轮次: {args.max_rounds}")
        
        system = EnhancedMultiAgentSystem(
            model="Qwen/Qwen2.5-7B-Instruct",
            api_key=api_key,
            base_url=base_url,
            debate_threshold=args.threshold,
            max_debate_rounds=args.max_rounds,
            temperature=0.7
        )
        print("✅ 系统初始化成功!\n")
        
        # 如果命令行指定了股票代码，直接分析
        if args.symbol:
            print(f"开始增强版分析: {args.symbol}\n")
            result = system.run_analysis(args.symbol, verbose=not args.no_verbose)
            print_result(result)
            return
        
        # 交互循环
        while True:
            try:
                symbol = input("💬 请输入股票代码 (6位数字): ").strip()
                
                if not symbol:
                    continue
                
                if symbol.lower() in ['q', 'quit', 'exit', '退出']:
                    print("\n👋 感谢使用，再见!")
                    break
                
                # 验证股票代码格式
                if not symbol.isdigit() or len(symbol) != 6:
                    print("❌ 股票代码格式错误，请输入6位数字 (如: 600519)")
                    continue
                
                # 运行增强版分析
                print(f"\n🚀 开始增强版分析: {symbol}")
                print("⏳ 这可能需要1-2分钟，请耐心等待...\n")
                result = system.run_analysis(symbol, verbose=not args.no_verbose)
                print_result(result)
                
            except KeyboardInterrupt:
                print("\n\n👋 程序被中断，再见!")
                break
            except Exception as e:
                print(f"\n❌ 发生错误: {str(e)}")
                print("请重试或联系管理员\n")
    
    except Exception as e:
        print(f"\n❌ 初始化失败: {str(e)}")
        print("请检查配置文件或网络连接\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
