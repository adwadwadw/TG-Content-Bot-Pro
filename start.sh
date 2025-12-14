#!/bin/sh

# 极速启动脚本 - TG Content Bot Pro

echo "🚀 启动TG Content Bot Pro应用..."

# 设置环境变量
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# 禁用可能的调试服务器
export FLASK_DEBUG=0
export DJANGO_DEBUG=0

# 启动应用
cd /app && python3 -m main