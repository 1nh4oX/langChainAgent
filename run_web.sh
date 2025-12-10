#!/bin/bash
# 启动 Vercel 风格的 Web 应用 (本地开发模式)

echo "🚀 正在启动 AI Trading Agent (Web版)..."
echo "🌐 访问地址: http://localhost:8000"
echo "📝 API文档: http://localhost:8000/docs"

# 激活虚拟环境
source venv/bin/activate

# 设置 PYTHONPATH 确保能找到 src
export PYTHONPATH=$PYTHONPATH:$(pwd)/vercel_app/api

# 运行 FastAPI 应用
python vercel_app/api/index.py
