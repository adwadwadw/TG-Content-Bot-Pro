FROM ghcr.io/liwoyuandiane/tg-content-bot-pro:main

# 设置工作目录
WORKDIR /app

# 复制应用代码（从基础镜像继承）
# 基础镜像已经包含了所有必要的文件

# 暴露健康检查端口
EXPOSE 8080

# 健康检查 - 简化版本，只检查进程是否运行
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD ps aux | grep python | grep -v grep || exit 1

# 启动命令（与main分支保持一致）
CMD ["sh", "start.sh"]
