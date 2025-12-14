FROM ghcr.io/liwoyuandiane/tg-content-bot-pro:main

# 极简部署版本 - 使用预构建的多架构镜像
LABEL maintainer="liwoyuandiane"
LABEL description="TG Content Bot Pro - 极速部署版本"

# 设置工作目录（继承基础镜像）
WORKDIR /app

# 暴露健康检查端口
EXPOSE 8089

# 健康检查 - 使用HTTP健康检查接口
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8089/health || exit 1

# 启动命令
CMD ["sh", "start.sh"]