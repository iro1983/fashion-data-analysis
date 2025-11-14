#!/bin/bash
# 启动脚本 - Railway部署

# 设置环境变量
export PYTHONPATH=/workspace
export PORT=${PORT:-8000}

# 安装依赖
echo "📦 安装Python依赖..."
pip install -r requirements.txt

# 启动应用
echo "🚀 启动Web应用..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT