FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    curl \
    build-essential \
    python3-dev \
    libssl-dev \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# 升级pip并设置镜像源
RUN pip install --upgrade pip && \
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖（分步安装，避免冲突）
RUN pip install --no-cache-dir cryptography==41.0.7 && \
    pip install --no-cache-dir pymongo==4.5.0 && \
    pip install --no-cache-dir dnspython==2.4.2 && \
    pip install --no-cache-dir python-decouple==3.8 && \
    pip install --no-cache-dir nest-asyncio==1.5.8 && \
    pip install --no-cache-dir telethon==1.28.5 && \
    pip install --no-cache-dir pyrogram==2.0.106 && \
    pip install --no-cache-dir ethon==0.1.4 && \
    pip install --no-cache-dir cryptg==0.4.0 && \
    pip install --no-cache-dir tgcrypto==1.2.5

# 复制应用代码（排除不必要的文件）
COPY main/ ./
COPY start.sh .
COPY .dockerignore .

# 设置执行权限
RUN chmod +x start.sh

# 暴露健康检查端口
EXPOSE 8080

# 健康检查 - 简化版本，只检查进程是否运行
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD ps aux | grep python | grep -v grep || exit 1

# 启动命令
CMD ["sh", "start.sh"]
