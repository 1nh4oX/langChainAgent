#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stock Analysis Agent - Main Application
股票分析 Agent - 主应用程序

这是项目的主入口文件，提供交互式命令行界面
"""

import sys
from src.agent import StockAnalysisAgent
from src.config import get_settings


def print_welcome():
    """打印欢迎信息"""
    print("=" * 70)
    print("              🤖 A股智能分析 Agent 系统")
    print("=" * 70)
    print("\n功能说明:")
    print("  - 📊 历史行情查询")
    print("  - 📰 新闻资讯获取")
    print("  - 📈 技术指标分析")
    print("  - 🏢 行业对比分析")
    print("  - 🎯 综合智能分析")
    print("\n示例查询:")
    print("  • 查询贵州茅台（600519）的最新情况")
    print("  • 分析平安银行的技术指标")
    print("  • 获取招商银行的最新新闻")
    print("\n输入 'q' 或 'quit' 退出程序")
    print("=" * 70 + "\n")


def main():
    """主函数"""
    # 打印欢迎信息
    print_welcome()
    
    try:
        # 加载配置
        settings = get_settings()
        
        # 检查 API 配置
        if not settings.api_key or not settings.base_url:
            print("⚠️  警告: 未配置 API 密钥！")
            print("请创建 .env 文件并配置以下内容:")
            print("  api-key=你的API密钥")
            print("  base-url=API基础URL")
            print("\n详见 .env.example 文件\n")
            return
        
        # 初始化 Agent
        print("🔧 正在初始化 Agent...")
        agent = StockAnalysisAgent(
            model=settings.model,
            api_key=settings.api_key,
            base_url=settings.base_url,
            temperature=settings.temperature,
            max_iterations=settings.max_iterations
        )
        print("✅ Agent 初始化成功！\n")
        
        # 交互循环
        while True:
            try:
                user_input = input("💬 请输入您的问题: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['q', 'quit', 'exit', '退出']:
                    print("\n👋 感谢使用，再见！")
                    break
                
                # 运行 Agent
                print("\n🤔 Agent 正在思考...")
                print("-" * 70)
                
                result = agent.run(user_input, verbose=True)
                
                print("-" * 70)
                print("\n📊 分析结果:")
                print("=" * 70)
                print(result['output'])
                print("=" * 70)
                print(f"\n💡 执行迭代次数: {result['iterations']}\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 程序被中断，再见！")
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




