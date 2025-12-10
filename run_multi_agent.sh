#!/bin/bash
# 多Agent股票分析系统 - 启动脚本

echo "=========================================="
echo "   多Agent股票交易分析系统"
echo "=========================================="
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在!"
    echo "请先运行: python3 -m venv venv"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

echo "请选择启动模式:"
echo "  1) 命令行模式 (推荐首次使用)"
echo "  2) Web界面模式"
echo ""
read -p "请输入选择 (1或2): " choice

case $choice in
    1)
        echo ""
        echo "启动命令行模式..."
        echo "=========================================="
        python app_multi_agent.py
        ;;
    2)
        echo ""
        echo "启动Web界面模式..."
        echo "=========================================="
        echo "浏览器将自动打开 http://localhost:8501"
        echo ""
        streamlit run ui/streamlit_app_multi_agent.py
        ;;
    *)
        echo "无效选择!"
        exit 1
        ;;
esac
