#!/bin/bash
# Stock Analysis Agent - UI 启动脚本

echo "=================================="
echo "🚀 启动 Stock Analysis Agent UI"
echo "=================================="
echo ""

# 检查 streamlit 是否安装
if ! command -v streamlit &> /dev/null
then
    echo "❌ Streamlit 未安装"
    echo "正在安装..."
    pip install streamlit
    echo ""
fi

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  警告: 未找到 .env 文件"
    echo "请先配置 API 密钥:"
    echo "  cp .env.example .env"
    echo "  然后编辑 .env 文件填入你的 API 密钥"
    echo ""
    read -p "是否继续？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]
    then
        exit 1
    fi
fi

echo "✅ 环境检查完成"
echo "🌐 正在启动 Web UI..."
echo ""
echo "访问地址: http://localhost:8501"
echo "按 Ctrl+C 停止服务"
echo ""
echo "=================================="

# 启动 streamlit
streamlit run ui/streamlit_app.py


