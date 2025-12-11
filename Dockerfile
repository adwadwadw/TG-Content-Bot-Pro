FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露健康检查端口
EXPOSE 8080

# 健康检查 - 简化版本，只检查进程是否运行
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD ps aux | grep python | grep -v grep || exit 1

# 复制启动脚本
COPY start.sh .

# 启动命令
CMD ["sh", "start.sh"]
