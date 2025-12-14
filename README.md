# TG Content Bot Pro - 极速部署版

> 🚀 专为快速部署优化的Telegram内容机器人

**TG Content Bot Pro** 是一个功能强大的Telegram机器人，专门用于克隆和保存来自公开和私密频道的消息内容。本分支为**极速部署版**，使用预构建的多架构Docker镜像，实现秒级部署。

[![Docker Image](https://img.shields.io/badge/docker-ready-blue?logo=docker)](https://github.com/liwoyuandiane/TG-Content-Bot-Pro/pkgs/container/tg-content-bot-pro)
[![Multi-Arch](https://img.shields.io/badge/multi--arch-linux%2Famd64%2C%20linux%2Farm64-green)](https://github.com/liwoyuandiane/TG-Content-Bot-Pro/pkgs/container/tg-content-bot-pro)
[![GitHub](https://img.shields.io/badge/GitHub-Deploy%20Branch-brightgreen)](https://github.com/liwoyuandiane/TG-Content-Bot-Pro/tree/pull)

## ✨ 核心特性

- ✅ **极速部署** - 仅需6个文件，下载即用
- ✅ **多架构支持** - 自动适配x86/ARM服务器
- ✅ **健康监控** - 内置HTTP健康检查接口
- ✅ **资源优化** - 内存占用小于512MB
- ✅ **自动更新** - 使用最新的稳定镜像版本
- ✅ **安全保障** - GitHub官方容器注册表

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆部署分支（文件极少，下载快速）
git clone -b pull https://github.com/liwoyuandiane/TG-Content-Bot-Pro.git
cd TG-Content-Bot-Pro
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件
nano .env  # 或使用您喜欢的编辑器
```

### 3. 一键启动

```bash
# 使用Docker Compose启动
docker-compose up -d

# 验证应用状态
curl http://localhost:8089/health
```

## 📋 配置说明

### 必需环境变量

| 变量名 | 说明 | 获取方式 | 必需 |
|--------|------|---------|------|
| `API_ID` | Telegram API ID | [my.telegram.org](https://my.telegram.org) | ✅ |
| `API_HASH` | Telegram API Hash | [my.telegram.org](https://my.telegram.org) | ✅ |
| `BOT_TOKEN` | 机器人Token | [@BotFather](https://t.me/BotFather) | ✅ |
| `AUTH` | 授权用户ID | [@userinfobot](https://t.me/userinfobot) | ✅ |
| `MONGO_DB` | MongoDB连接字符串 | [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) | ✅ |

### 可选环境变量

- `SESSION` - Pyrogram会话字符串（增强功能）
- `FORCESUB` - 强制订阅频道（格式：`@channel_username`）
- `HEALTH_CHECK_PORT` - 健康检查端口（默认：8080）

## 🔧 部署方式

### Docker Compose（推荐）

```yaml
# docker-compose.yml 已优化配置
services:
  tg-content-bot:
    image: ghcr.io/liwoyuandiane/tg-content-bot-pro:main
    restart: unless-stopped
    environment:
      - API_ID=${API_ID}
      - API_HASH=${API_HASH}
      - BOT_TOKEN=${BOT_TOKEN}
      - AUTH=${AUTH}
      - MONGO_DB=${MONGO_DB}
    ports:
      - "8080:8080"
```

### 直接Docker运行

```bash
docker run -d \
  --name tg-content-bot \
  -p 8080:8080 \
  -e API_ID=your_api_id \
  -e API_HASH=your_api_hash \
  -e BOT_TOKEN=your_bot_token \
  -e AUTH=your_user_id \
  -e MONGO_DB=your_mongo_connection \
  ghcr.io/liwoyuandiane/tg-content-bot-pro:main
```

## 🛠️ 运维管理

### 容器管理

```bash
# 查看容器状态
docker-compose ps

# 查看实时日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down
```

### 健康检查

应用提供完整的健康监控：

```bash
# HTTP健康检查
curl http://localhost:8080/health

# 状态页面
curl http://localhost:8080/
```

### 日志查看

```bash
# 查看最新日志
docker logs tg-content-bot

# 实时跟踪日志
docker logs -f tg-content-bot

# 查看特定时间段的日志
docker logs --since 1h tg-content-bot
```

## 🤖 机器人功能

### 核心命令

- `/start` - 初始化机器人并显示欢迎信息
- `/help` - 获取详细的使用帮助
- `/batch` - 批量下载消息（最多100条，仅所有者）
- `/traffic` - 查看个人流量统计
- `/stats` - 查看机器人整体统计（仅所有者）

### 消息克隆

发送任意Telegram消息链接到机器人，自动下载内容并发送给您：
- 支持文本、图片、视频、文件等多种格式
- 自动处理权限验证
- 智能重试机制

## 🏗️ 技术架构

### 分支策略

| 分支 | 用途 | 特点 |
|------|------|------|
| **main** | 开发构建 | 完整的Docker构建流程，包含所有源代码 |
| **pull** | 生产部署 | 极简部署，使用预构建镜像，快速启动 |

### 文件结构

```
TG-Content-Bot-Pro/
├── .env.example          # 环境变量模板
├── docker-compose.yml    # Docker编排配置
├── Dockerfile            # 极简Docker配置
├── README.md             # 部署文档
├── start.sh              # 启动脚本
└── .codebuddy/           # 开发工具配置
```

## 🔒 安全说明

- 使用GitHub官方容器注册表，确保镜像来源可靠
- 所有镜像经过多架构测试
- 自动使用最新安全补丁
- 内置资源限制，防止资源滥用

## 📞 支持与反馈

如果遇到问题或有建议，请通过以下方式联系：
- GitHub Issues: [提交问题](https://github.com/liwoyuandiane/TG-Content-Bot-Pro/issues)
- Telegram: 通过机器人反馈

---

**部署分支维护者**: [liwoyuandiane](https://github.com/liwoyuandiane)
**最后更新**: 2025年12月

- **main分支**：开发构建，包含完整源代码
- **pull分支**：极简部署，仅包含部署文件

**镜像地址**：`ghcr.io/liwoyuandiane/tg-content-bot-pro:main`

---

## 📄 许可证

本项目基于MIT许可证开源。