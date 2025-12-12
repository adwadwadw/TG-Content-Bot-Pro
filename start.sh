#!/bin/bash

# 设置环境变量
export PYTHONUNBUFFERED=1
export PYTHONPATH=/app:$PYTHONPATH

# 启动应用
echo "启动TG Content Bot Pro应用..."
cd /app

# 直接使用主入口文件启动
python3 __main__.py