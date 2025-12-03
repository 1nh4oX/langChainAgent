"""
News Collection Script
新闻数据采集脚本

功能：采集100条A股市场新闻数据，保存为CSV和JSON格式
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import akshare as ak
import pandas as pd
from datetime import datetime
import time

from src.utils import save_to_csv, save_to_json
from src.config import get_settings


def collect_stock_news(num_stocks=10, news_per_stock=10):
    """
    采集多只股票的新闻数据
    
    Args:
        num_stocks: 采集的股票数量
        news_per_stock: 每只股票采集的新闻数量
    
    Returns:
        DataFrame: 包含所有新闻的数据框
    """
    print("=" * 60)
    print("📰 开始采集A股新闻数据")
    print("=" * 60)
    
    # 热门A股股票代码列表
    popular_stocks = [
        ("600519", "贵州茅台"),
        ("000001", "平安银行"),
        ("600036", "招商银行"),
        ("000858", "五粮液"),
        ("600276", "恒瑞医药"),
        ("601318", "中国平安"),
        ("000002", "万科A"),
        ("600887", "伊利股份"),
        ("000333", "美的集团"),
        ("601166", "兴业银行"),
        ("600030", "中信证券"),
        ("601888", "中国中免"),
        ("300750", "宁德时代"),
        ("600031", "三一重工"),
        ("000725", "京东方A"),
    ]
    
    all_news = []
    successful_stocks = 0
    
    for idx, (stock_code, stock_name) in enumerate(popular_stocks[:num_stocks], 1):
        print(f"\n[{idx}/{num_stocks}] 正在采集 {stock_name}({stock_code}) 的新闻...")
        
        try:
            df_news = ak.stock_news_em(symbol=stock_code)
            
            if df_news.empty:
                print(f"  ⚠️  {stock_name} 暂无新闻数据")
                continue
            
            df_news = df_news.head(news_per_stock)
            df_news['股票代码'] = stock_code
            df_news['股票名称'] = stock_name
            
            all_news.append(df_news)
            successful_stocks += 1
            
            print(f"  ✅ 成功采集 {len(df_news)} 条新闻")
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  ❌ 采集失败: {str(e)}")
            continue
    
    if not all_news:
        print("\n❌ 未能采集到任何新闻数据！")
        return None
    
    df_all = pd.concat(all_news, ignore_index=True)
    
    print("\n" + "=" * 60)
    print(f"✅ 采集完成！共采集 {len(df_all)} 条新闻（来自 {successful_stocks} 只股票）")
    print("=" * 60)
    
    return df_all


def save_news_data(df, output_dir="data/raw"):
    """保存新闻数据"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 创建输出目录
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 保存为 CSV
    csv_file = f"{output_dir}/stock_news_{timestamp}.csv"
    save_to_csv(df, csv_file)
    
    # 保存为 JSON
    json_file = f"{output_dir}/stock_news_{timestamp}.json"
    save_to_json(df, json_file)
    
    # 生成统计报告
    report_file = f"{output_dir}/news_report_{timestamp}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("新闻数据采集报告\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"采集时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"新闻总数: {len(df)} 条\n")
        f.write(f"涉及股票: {df['股票代码'].nunique()} 只\n\n")
        
        f.write("各股票新闻数量:\n")
        f.write("-" * 40 + "\n")
        stock_counts = df.groupby(['股票名称', '股票代码']).size().sort_values(ascending=False)
        for (name, code), count in stock_counts.items():
            f.write(f"{name}({code}): {count} 条\n")
    
    print(f"📁 统计报告已保存: {report_file}")
    
    return csv_file, json_file


def main():
    """主函数"""
    print("\n🚀 A股新闻数据采集工具\n")
    
    # 采集新闻
    df_news = collect_stock_news(num_stocks=10, news_per_stock=10)
    
    if df_news is not None and not df_news.empty:
        # 保存数据
        csv_file, json_file = save_news_data(df_news)
        
        print("\n✅ 所有任务完成！")
        print(f"💾 共采集 {len(df_news)} 条新闻数据")
    else:
        print("\n❌ 采集失败，请检查网络连接或稍后重试")


if __name__ == "__main__":
    main()


