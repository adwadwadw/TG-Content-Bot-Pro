#!/bin/bash

# 极速启动脚本 - TG Content Bot Pro

echo "🚀 启动TG Content Bot Pro应用..."
cd /app

# 设置环境变量
export PYTHONUNBUFFERED=1

# 启动应用
python3 -c "from main.app import main; main()"