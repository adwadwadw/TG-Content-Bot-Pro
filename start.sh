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

# 添加调试信息
echo "当前目录: $(pwd)"
echo "Python版本: $(python3 --version)"
echo "Python路径: $(which python3)"

# 检查环境变量
echo "检查环境变量..."
if [ -f ".env" ]; then
    echo "找到.env文件"
    grep -E "BOT_TOKEN|API_ID|API_HASH" .env | head -3
else
    echo "未找到.env文件"
fi

# 直接启动应用，添加超时控制
echo "开始启动应用..."
python3 -c "
import asyncio
import sys
import signal
from main.app import main

# 设置超时（10分钟）
def timeout_handler(signum, frame):
    print('⚠️ 启动超时，强制退出...')
    sys.exit(1)

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(600)  # 10分钟超时

try:
    main()
except KeyboardInterrupt:
    print('\\n收到中断信号，退出应用')
except Exception as e:
    print(f'启动失败: {e}')
    sys.exit(1)
finally:
    signal.alarm(0)  # 取消超时
"