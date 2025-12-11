# TG Content Bot Pro - 部署分支

> 极简部署版本 - 使用预构建的多架构镜像

这是TG Content Bot Pro的**部署分支**，专门用于快速部署。无需重新构建，直接使用GitHub Actions自动构建的多架构镜像。

[![Docker Image](https://img.shields.io/badge/docker-ready-blue?logo=docker)](https://github.com/liwoyuandiane/TG-Content-Bot-Pro/pkgs/container/tg-content-bot-pro)
[![Multi-Arch](https://img.shields.io/badge/multi--arch-linux%2Famd64%2C%20linux%2Farm64-green)](https://github.com/liwoyuandiane/TG-Content-Bot-Pro/pkgs/container/tg-content-bot-pro)

## 🚀 极速部署

本分支仅包含部署所需的最少文件，专注于快速部署体验。

### 一键部署

```bash
# 克隆部署分支（文件极少，下载快速）
git clone -b pull https://github.com/liwoyuandiane/TG-Content-Bot-Pro.git
cd TG-Content-Bot-Pro

# 配置环境变量
cp .env.example .env
nano .env  # 编辑配置

# 一键启动（使用预构建的多架构镜像）
docker-compose up -d

# 检查应用状态
curl http://localhost:8080/health
```

## 📋 环境配置

### 必需环境变量

复制环境变量模板并编辑配置：

```bash
cp .env.example .env
nano .env
```

**必需配置**：
- `API_ID` - Telegram API ID ([获取地址](https://my.telegram.org))
- `API_HASH` - Telegram API Hash ([获取地址](https://my.telegram.org))
- `BOT_TOKEN` - 机器人Token ([@BotFather](https://t.me/BotFather))
- `AUTH` - 授权用户ID ([@userinfobot](https://t.me/userinfobot))
- `MONGO_DB` - MongoDB连接字符串 ([MongoDB Atlas](https://www.mongodb.com/cloud/atlas))

**可选配置**：
- `SESSION` - Pyrogram会话字符串
- `FORCESUB` - 强制订阅频道
- `HEALTH_CHECK_PORT` - 健康检查端口（默认8080）

## 🔍 健康检查

应用内置HTTP健康检查功能：
- **健康检查**：`http://localhost:8080/health`
- **状态页面**：`http://localhost:8080/`
- **Docker监控**：自动健康检查，失败自动重启

## 🛠️ 容器管理

```bash
# 查看容器状态
docker-compose ps

# 查看实时日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart
```

## 🎯 部署优势

- 🚀 **快速部署**：只有4个文件，下载秒完成
- 🏗️ **多架构支持**：支持x86和ARM架构服务器
- 🔍 **健康监控**：内置HTTP健康检查
- 📦 **版本控制**：自动使用最新稳定镜像
- 🔒 **安全可靠**：使用GitHub官方容器注册表

## 📖 基本使用

### 机器人命令
- `/start` - 初始化机器人
- `/batch` - 批量下载消息（最多100条）
- `/traffic` - 查看流量统计
- `/stats` - 查看机器人统计（仅所有者）

### 消息克隆
发送任意Telegram消息链接到机器人，自动下载并发送给您。

---

## 🌿 分支策略

- **main分支**：开发构建，包含完整源代码
- **pull分支**：极简部署，仅包含部署文件

**镜像地址**：`ghcr.io/liwoyuandiane/tg-content-bot-pro:main`

---

## 📄 许可证

本项目基于MIT许可证开源。