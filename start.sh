#!/bin/bash

# 设置环境变量
export PYTHONUNBUFFERED=1

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 启动应用
echo "启动TG Content Bot Pro应用..."
cd "$SCRIPT_DIR"

# 检查是否在虚拟环境中
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 直接启动应用
python3 -c "from main.app import main; main()"