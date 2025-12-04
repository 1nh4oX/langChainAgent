"""
Basic Usage Example
基础使用示例
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agent import StockAnalysisAgent


def example_1_simple_query():
    """示例1: 简单查询"""
    print("\n" + "="*60)
    print("示例1: 简单查询股票信息")
    print("="*60)
    
    agent = StockAnalysisAgent()
    result = agent.run("查询贵州茅台（600519）的最新价格")
    
    print(f"\n结果:\n{result['output']}")
    print(f"\n迭代次数: {result['iterations']}")


def example_2_technical_analysis():
    """示例2: 技术分析"""
    print("\n" + "="*60)
    print("示例2: 技术指标分析")
    print("="*60)
    
    agent = StockAnalysisAgent()
    result = agent.run("分析平安银行（000001）的技术指标，包括均线走势")
    
    print(f"\n结果:\n{result['output']}")
    print(f"\n迭代次数: {result['iterations']}")


def example_3_news_analysis():
    """示例3: 新闻分析"""
    print("\n" + "="*60)
    print("示例3: 获取新闻资讯")
    print("="*60)
    
    agent = StockAnalysisAgent()
    result = agent.run("获取招商银行（600036）的最新新闻，有哪些重要信息")
    
    print(f"\n结果:\n{result['output']}")
    print(f"\n迭代次数: {result['iterations']}")


def example_4_comprehensive():
    """示例4: 综合分析"""
    print("\n" + "="*60)
    print("示例4: 综合分析")
    print("="*60)
    
    agent = StockAnalysisAgent()
    result = agent.run(
        "对五粮液（000858）进行全面分析，包括历史走势、技术指标、基本面和新闻"
    )
    
    print(f"\n结果:\n{result['output']}")
    print(f"\n迭代次数: {result['iterations']}")


def example_5_batch_analysis():
    """示例5: 批量分析"""
    print("\n" + "="*60)
    print("示例5: 批量分析多只股票")
    print("="*60)
    
    agent = StockAnalysisAgent()
    stocks = [
        ("600519", "贵州茅台"),
        ("000001", "平安银行"),
        ("600036", "招商银行")
    ]
    
    for code, name in stocks:
        print(f"\n--- 分析 {name}({code}) ---")
        result = agent.run(f"简要分析{name}（{code}）的最新情况", verbose=False)
        print(result['output'][:200] + "...")  # 只显示前200字


def example_6_custom_config():
    """示例6: 自定义配置"""
    print("\n" + "="*60)
    print("示例6: 使用自定义配置")
    print("="*60)
    
    # 自定义 Agent 配置
    agent = StockAnalysisAgent(
        model="Qwen/Qwen2.5-7B-Instruct",
        temperature=0.5,  # 更高的温度，输出更有创造性
        max_iterations=5  # 限制最大迭代次数
    )
    
    result = agent.run("分析恒瑞医药（600276）的投资价值")
    print(f"\n结果:\n{result['output']}")
    print(f"\n迭代次数: {result['iterations']}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Stock Analysis Agent - 使用示例")
    print("="*60)
    
    # 运行示例（可以注释掉不需要的）
    try:
        example_1_simple_query()
        # example_2_technical_analysis()
        # example_3_news_analysis()
        # example_4_comprehensive()
        # example_5_batch_analysis()
        # example_6_custom_config()
        
        print("\n" + "="*60)
        print("✅ 所有示例运行完成！")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        print("请检查配置和网络连接\n")




