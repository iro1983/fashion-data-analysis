#!/bin/bash
# Railway部署启动脚本
set -e

# 设置环境变量
export PYTHONPATH=/app:$PYTHONPATH
export PORT=${PORT:-8000}

echo "🚀 启动时尚数据分析系统..."
echo "📦 安装依赖..."

# 安装依赖
pip install --no-cache-dir -r requirements.txt

echo "✅ 依赖安装完成"
echo "🌐 启动Web应用在端口 $PORT..."

# 启动应用
python main.py