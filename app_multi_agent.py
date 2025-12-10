#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Multi-Agent Stock Analysis - Command Line Interface
多Agent股票分析系统 - 命令行入口

提供命令行交互界面进行多Agent分析
"""

import sys
import argparse
from src.agent.multi_agent_system import MultiAgentTradingSystem
from src.config import get_settings


def print_welcome():
    """打印欢迎信息"""
    print("=" * 70)
    print("           🤖 多Agent股票交易分析系统")
    print("=" * 70)
    print("\n系统架构:")
    print("  1️⃣  数据分析师 - 获取数据并基础分析")
    print("  2️⃣  新闻研究员 - 搜索新闻并深度分析")
    print("  3️⃣  多头评审 - 从看涨角度评审")
    print("  4️⃣  空头评审 - 从看跌角度评审")
    print("  5️⃣  辩论协调 - 组织辩论并形成共识")
    print("\n特色功能:")
    print("  🗣️  智能辩论: 评分差异超过阈值自动触发辩论")
    print("  📊 完整记录: 保存每个Agent的工作过程")
    print("  🎯 中文辩论: 所有分析和辩论使用中文")
    print("\n输入 'q' 或 'quit' 退出程序")
    print("=" * 70 + "\n")


def print_result(result):
    """格式化打印分析结果"""
    print("\n" + "=" * 70)
    print("📊 最终分析报告")
    print("=" * 70)
    
    print(f"\n股票代码: {result.symbol}")
    print(f"最终建议: {result.final_recommendation}")
    print(f"信心水平: {result.confidence}")
    
    print(f"\n关键评分:")
    print(f"  数据分析: {result.key_data.get('data_analyst_score', 'N/A')}/10")
    print(f"  多头评审: {result.key_data.get('bull_score', 'N/A')}/10")
    print(f"  空头评审: {result.key_data.get('bear_score', 'N/A')}/10")
    print(f"  评分差异: {result.key_data.get('score_diff', 'N/A')}")
    
    if result.debate_occurred:
        print(f"\n💬 辩论情况: 已进行 {len(result.debate_rounds)} 轮辩论")
    else:
        print(f"\n✅ 无需辩论: 评分接近")
    
    print(f"\n" + "-" * 70)
    print("简要分析:")
    print("-" * 70)
    print(result.brief_analysis)
    
    # 展开各Agent工作详情
    print(f"\n" + "=" * 70)
    print("📋 各Agent工作详情")
    print("=" * 70)
    
    for output in result.all_agent_outputs:
        print(f"\n【{output.role.value}】 ({output.timestamp})")
        if output.score:
            print(f"评分: {output.score}/10")
        print("-" * 50)
        print(output.content)
    
    # 辩论详情
    if result.debate_rounds:
        print(f"\n" + "=" * 70)
        print("🗣️  辩论详情")
        print("=" * 70)
        
        for debate in result.debate_rounds:
            print(f"\n【第 {debate.round_number} 轮辩论】 ({debate.timestamp})")
            print("\n主持人引导:")
            print(debate.moderator_summary)
            print("\n多头论证:")
            print(debate.bull_argument)
            print("\n空头论证:")
            print(debate.bear_argument)
            print("-" * 70)
    
    print("\n" + "=" * 70)
    print(f"✅ 分析完成! 时间: {result.timestamp}")
    print("=" * 70 + "\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='多Agent股票交易分析系统')
    parser.add_argument('--symbol', '-s', type=str, help='股票代码')
    parser.add_argument('--threshold', '-t', type=float, default=3.0, 
                       help='辩论触发阈值 (默认: 3.0)')
    parser.add_argument('--max-rounds', '-r', type=int, default=3,
                       help='最大辩论轮次 (默认: 3)')
    parser.add_argument('--no-verbose', action='store_true',
                       help='不显示详细过程')
    
    args = parser.parse_args()
    
    # 打印欢迎信息
    print_welcome()
    
    try:
        # 加载配置
        settings = get_settings()
        
        # 使用硅基流动API (测试阶段)
        api_key = "sk-glrkmcbkaybtvlnnvmvcakrchncpwadpxeibzitkpkgepueh"
        base_url = "https://api.siliconflow.cn/v1"
        
        # 初始化多Agent系统
        print("🔧 正在初始化多Agent系统...")
        print(f"   分析模型: Qwen/Qwen2.5-7B-Instruct")
        print(f"   辩论模型: Qwen/Qwen2.5-7B-Instruct (相同)")
        print(f"   辩论阈值: {args.threshold}")
        print(f"   最大轮次: {args.max_rounds}")
        
        system = MultiAgentTradingSystem(
            analysis_model="Qwen/Qwen2.5-7B-Instruct",
            analysis_api_key=api_key,
            analysis_base_url=base_url,
            use_same_model=True,
            debate_threshold=args.threshold,
            max_debate_rounds=args.max_rounds,
            temperature=0.7
        )
        print("✅ 系统初始化成功!\n")
        
        # 如果命令行指定了股票代码，直接分析
        if args.symbol:
            print(f"开始分析股票: {args.symbol}\n")
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
                
                # 运行分析
                print(f"\n开始分析股票: {symbol}")
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
