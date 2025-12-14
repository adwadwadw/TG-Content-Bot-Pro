#!/bin/bash

# 设置环境变量
export PYTHONUNBUFFERED=1

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 启动应用
echo "🚀 启动TG Content Bot Pro应用..."

# 检查是否在虚拟环境中
if [ -d "venv" ]; then
    echo "📦 激活虚拟环境..."
    source venv/bin/activate
fi

# 添加调试信息
echo "📂 当前目录: $(pwd)"
echo "🐍 Python版本: $(python3 --version)"
echo "📍 Python路径: $(which python3)"

# 检查环境变量配置（云平台通常通过环境变量而非.env文件配置）
echo "🔍 检查环境变量配置..."

# 检查必需的环境变量
MISSING_VARS=""
[ -z "$API_ID" ] && MISSING_VARS="$MISSING_VARS API_ID"
[ -z "$API_HASH" ] && MISSING_VARS="$MISSING_VARS API_HASH"
[ -z "$BOT_TOKEN" ] && MISSING_VARS="$MISSING_VARS BOT_TOKEN"
[ -z "$AUTH" ] && MISSING_VARS="$MISSING_VARS AUTH"
[ -z "$MONGO_DB" ] && MISSING_VARS="$MISSING_VARS MONGO_DB"

if [ -n "$MISSING_VARS" ]; then
    echo "❌ 缺少必需的环境变量:$MISSING_VARS"
    echo "💡 请在环境变量中设置以下变量："
    echo "   - API_ID: Telegram API ID"
    echo "   - API_HASH: Telegram API Hash"
    echo "   - BOT_TOKEN: Telegram Bot Token"
    echo "   - AUTH: 授权用户ID"
    echo "   - MONGO_DB: MongoDB连接字符串"
    echo ""
    echo "📝 在Render等平台上，请在项目设置的Environment Variables中配置这些变量"
    echo "📄 或者挂载包含这些变量的.env文件到容器中"
    exit 1
else
    echo "✅ 所有必需的环境变量已配置"
fi

# 检查.env文件（本地开发使用）
if [ -f ".env" ]; then
    echo "📄 检测到.env文件，将从中加载环境变量..."
    # 注意：在云平台上通常不需要.env文件，环境变量由平台管理
fi

# 启动应用
echo "🤖 开始启动机器人应用..."
echo "📡 连接到Telegram服务器..."
python3 -m main