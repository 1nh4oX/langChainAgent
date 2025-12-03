"""
Custom Tool Example
自定义工具示例
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from langchain_core.tools import tool
from src.agent import StockAnalysisAgent


# 定义自定义工具
@tool
def get_market_sentiment(query: str) -> str:
    """
    获取市场情绪指标（示例工具）
    
    Args:
        query: 查询内容
        
    Returns:
        市场情绪分析
    """
    # 这里是示例实现，实际应该调用真实的数据接口
    return """市场情绪分析（示例数据）:
- 恐慌贪婪指数: 55 (中性)
- 市场热度: 偏热
- 成交量: 较前日增长15%
- 涨跌比: 1.2:1
- 建议: 保持谨慎乐观
"""


@tool
def calculate_risk_score(symbol: str) -> str:
    """
    计算股票风险评分（示例工具）
    
    Args:
        symbol: 股票代码
        
    Returns:
        风险评分
    """
    # 示例实现
    return f"""风险评分分析（示例数据 - {symbol}）:
- 波动率风险: 中等 (3/5)
- 流动性风险: 低 (2/5)
- 估值风险: 中等 (3/5)
- 行业风险: 低 (2/5)
- 综合风险评分: 2.5/5 (中低风险)
"""


def main():
    """主函数"""
    print("\n" + "="*60)
    print("自定义工具示例")
    print("="*60)
    
    # 1. 创建 Agent
    agent = StockAnalysisAgent()
    
    # 2. 添加自定义工具
    print("\n📝 添加自定义工具...")
    agent.add_tool(get_market_sentiment)
    agent.add_tool(calculate_risk_score)
    print("✅ 工具添加成功！")
    
    # 3. 使用新工具
    print("\n" + "="*60)
    print("测试1: 使用市场情绪工具")
    print("="*60)
    
    result1 = agent.run("当前A股市场的整体情绪如何？")
    print(f"\n结果:\n{result1['output']}")
    
    print("\n" + "="*60)
    print("测试2: 使用风险评分工具")
    print("="*60)
    
    result2 = agent.run("分析贵州茅台（600519）的风险评分")
    print(f"\n结果:\n{result2['output']}")
    
    print("\n" + "="*60)
    print("测试3: 综合使用所有工具")
    print("="*60)
    
    result3 = agent.run(
        "对平安银行（000001）进行全面分析，包括历史数据、风险评分和市场情绪"
    )
    print(f"\n结果:\n{result3['output']}")
    
    print("\n✅ 所有测试完成！")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")


