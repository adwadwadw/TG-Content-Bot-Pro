#!/bin/bash

# 设置环境变量
export PYTHONUNBUFFERED=1

# 启动应用
echo "启动TG Content Bot Pro应用..."
cd /app

# 直接启动应用
python3 main/__main__.py