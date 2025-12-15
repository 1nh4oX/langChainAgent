#!/bin/bash

# 🚀 局域网一键启动脚本
# 自动启动前后端服务

echo "🎓 大学局域网部署 - AI Stock Insight"
echo "=================================="
echo ""

# 获取局域网IP
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null)

if [ -z "$LOCAL_IP" ]; then
    echo "❌ 无法获取局域网IP，请检查网络连接"
    exit 1
fi

echo "📍 你的局域网IP: $LOCAL_IP"
echo ""
echo "📋 同学访问地址:"
echo "   前端: http://$LOCAL_IP:5173"
echo "   后端API文档: http://$LOCAL_IP:8000/docs"
echo ""
echo "⚠️  注意事项:"
echo "   1. 保持电脑不休眠"
echo "   2. 确保防火墙允许8000和5173端口"
echo "   3. 同学需要在同一局域网（连接同一WiFi）"
echo ""
echo "=================================="
echo ""

# 检查是否在项目目录
if [ ! -d "api" ] || [ ! -d "frontend" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 启动后端
echo "🔧 启动后端服务..."
cd api
python3 main.py &
BACKEND_PID=$!
echo "✅ 后端启动成功 (PID: $BACKEND_PID)"
cd ..

# 等待后端启动
sleep 3

# 启动前端
echo "🔧 启动前端服务..."
cd frontend
npm run dev -- --host 0.0.0.0 &
FRONTEND_PID=$!
echo "✅ 前端启动成功 (PID: $FRONTEND_PID)"
cd ..

echo ""
echo "🎉 服务启动完成！"
echo ""
echo "📱 告诉同学访问: http://$LOCAL_IP:5173"
echo ""
echo "💡 按 Ctrl+C 停止所有服务"
echo ""

# 等待用户中断
trap "echo ''; echo '🛑 正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo '✅ 服务已停止'; exit 0" INT

# 保持脚本运行
wait
