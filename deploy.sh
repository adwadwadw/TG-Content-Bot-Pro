#!/bin/bash

# TG Content Bot Pro - apply.build 部署脚本
# 适用于 apply.build 平台的自动化部署

echo "🚀 开始部署 TG Content Bot Pro..."

# 检查必需的环境变量
REQUIRED_VARS=("API_ID" "API_HASH" "BOT_TOKEN" "AUTH")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ 错误: 必需的环境变量 $var 未设置"
        echo "请确保以下环境变量已配置:"
        echo "- API_ID: Telegram API ID (从 my.telegram.org 获取)"
        echo "- API_HASH: Telegram API Hash (从 my.telegram.org 获取)" 
        echo "- BOT_TOKEN: 机器人Token (从 @BotFather 获取)"
        echo "- AUTH: 授权用户ID (从 @userinfobot 获取)"
        exit 1
    fi
    echo "✅ $var: 已配置"
done

# 设置默认值
HEALTH_CHECK_PORT=${HEALTH_CHECK_PORT:-8080}

# 创建环境文件
echo "📝 创建环境配置文件..."
cat > .env << EOF
# apply.build 自动生成的环境配置
API_ID=${API_ID}
API_HASH=${API_HASH}
BOT_TOKEN=${BOT_TOKEN}
AUTH=${AUTH}
MONGO_DB=${MONGO_DB:-}
SESSION=${SESSION:-}
FORCESUB=${FORCESUB:-}
HEALTH_CHECK_PORT=${HEALTH_CHECK_PORT}
EOF

echo "✅ 环境配置文件已创建"

# 启动应用
echo "🚀 启动 TG Content Bot Pro..."

# 使用Docker Compose部署
docker-compose up -d

if [ $? -eq 0 ]; then
    echo "✅ 部署成功!"
    echo ""
    echo "📊 应用信息:"
    echo "- 健康检查: http://localhost:${HEALTH_CHECK_PORT}/health"
    echo "- 状态页面: http://localhost:${HEALTH_CHECK_PORT}/"
    echo "- 容器状态: docker-compose ps"
    echo "- 查看日志: docker-compose logs -f"
    echo ""
    echo "🤖 机器人命令:"
    echo "- /start - 初始化机器人"
    echo "- /batch - 批量下载消息"
    echo "- /traffic - 查看流量统计"
    echo "- /stats - 查看机器人统计"
    echo ""
    echo "📖 使用说明:"
    echo "发送任意Telegram消息链接到机器人，即可自动下载并发送给您。"
else
    echo "❌ 部署失败，请检查日志"
    exit 1
fi