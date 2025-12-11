FROM ghcr.io/liwoyuandiane/tg-content-bot-pro:main

# 设置工作目录
WORKDIR /app

# 创建非root用户以提升安全性
RUN addgroup --system --gid 1001 appuser && \
    adduser --system --uid 1001 --gid 1001 appuser

# 复制应用代码（从基础镜像继承）
# 基础镜像已经包含了所有必要的文件

# 设置文件权限
RUN chown -R appuser:appuser /app

# 切换到非root用户
USER appuser

# 暴露健康检查端口
EXPOSE 8080

# 健康检查 - 兼容apply.build平台
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 启动命令（与main分支保持一致）
CMD ["sh", "start.sh"]
