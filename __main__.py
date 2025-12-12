#!/usr/bin/env python3
"""
TG Content Bot Pro - 主入口文件
为Northflank等平台提供兼容的启动入口
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入主应用
from main.__main__ import enhanced_main

if __name__ == "__main__":
    enhanced_main()