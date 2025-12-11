#!/bin/bash

# 设置环境变量
export PYTHONUNBUFFERED=1

# 等待数据库连接（如果需要）
if [ "$WAIT_FOR_DB" = "true" ]; then
    echo "等待数据库连接..."
    sleep 10
fi

# 启动应用
echo "启动TG Content Bot Pro应用..."
cd /app

# 检查是否有main模块
if [ -f "main/__main__.py" ]; then
    echo "使用模块方式启动..."
    python3 -m main "$@"
else
    echo "错误：找不到main模块"
    exit 1
fi

# 如果应用退出，记录退出状态
echo "应用退出，退出码: $?"
# 保持容器运行以便调试
sleep 3600