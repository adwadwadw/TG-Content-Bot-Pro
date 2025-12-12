#!/bin/bash

# 设置环境变量
export PYTHONUNBUFFERED=1
export PYTHONPATH=/app:$PYTHONPATH

# 启动应用
echo "启动TG Content Bot Pro应用..."
cd /app

# 检查Python路径和模块
echo "检查Python环境..."
python3 -c "import sys; print('Python路径:', sys.path)"
python3 -c "import os; print('当前目录:', os.getcwd())"
python3 -c "import os; print('文件列表:', os.listdir('.'))"

# 启动应用 - 使用绝对路径导入
python3 -c "
import sys
sys.path.insert(0, '/app')
from main import __main__
__main__.enhanced_main()
"