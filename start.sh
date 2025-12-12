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
    echo "✅ 找到.env文件"
    # 检查关键配置是否已设置
    if grep -q "your_api_id_here" .env || grep -q "your_bot_token_here" .env; then
        echo "⚠️ 警告：请先配置.env文件中的API_ID、API_HASH和BOT_TOKEN"
        echo "   否则应用无法连接到Telegram服务器"
        echo "   应用将以降级模式启动（仅健康检查服务）"
    fi
else
    echo "❌ 未找到.env文件，应用无法启动"
    echo "   请创建.env文件并配置必要的API凭证"
    exit 1
fi

# 直接启动应用，添加超时控制
echo "开始启动应用..."
python3 -c "
import asyncio
import sys
import signal
import os
from main.app import main

# 设置超时（5分钟）
def timeout_handler(signum, frame):
    print('⚠️ 启动超时，强制退出...')
    sys.exit(1)

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(300)  # 5分钟超时

try:
    main()
except KeyboardInterrupt:
    print('\\n收到中断信号，退出应用')
except Exception as e:
    print(f'启动失败: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    signal.alarm(0)  # 取消超时
"