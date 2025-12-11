# TG Content Bot Pro - apply.build 部署指南

## 🚀 快速部署

本项目已针对 apply.build 平台进行优化，支持一键部署。

### 部署方式

1. **直接部署（推荐）**
   - 在 apply.build 平台选择本项目仓库
   - 配置必需的环境变量
   - 点击部署即可

2. **手动部署**
   ```bash
   # 克隆项目
   git clone -b pull https://github.com/liwoyuandiane/TG-Content-Bot-Pro.git
   cd TG-Content-Bot-Pro
   
   # 运行部署脚本
   chmod +x deploy.sh
   ./deploy.sh
   ```

## 📋 环境变量配置

### 必需配置

| 变量名 | 描述 | 获取方式 |
|--------|------|----------|
| `API_ID` | Telegram API ID | [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | Telegram API Hash | [my.telegram.org](https://my.telegram.org) |
| `BOT_TOKEN` | 机器人Token | [@BotFather](https://t.me/BotFather) |
| `AUTH` | 授权用户ID | [@userinfobot](https://t.me/userinfobot) |

### 可选配置

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `MONGO_DB` | MongoDB连接字符串 | 空 |
| `SESSION` | Pyrogram会话字符串 | 空 |
| `FORCESUB` | 强制订阅频道用户名 | 空 |
| `HEALTH_CHECK_PORT` | 健康检查端口 | 8080 |

## 🔧 技术规格

- **运行时**: Docker 容器
- **架构**: 多架构支持 (x86/ARM)
- **健康检查**: HTTP 端口 8080
- **资源需求**: 最小 512MB 内存
- **网络**: 支持 Telegram API 访问

## 📊 部署验证

部署完成后，可以通过以下方式验证应用状态：

1. **健康检查**: `http://your-domain:8080/health`
2. **状态页面**: `http://your-domain:8080/`
3. **容器状态**: `docker-compose ps`
4. **实时日志**: `docker-compose logs -f`

## 🤖 功能特性

- ✅ 消息下载和转发
- ✅ 批量操作支持
- ✅ 流量统计
- ✅ 会话管理
- ✅ 健康监控
- ✅ 自动重启

## 🔒 安全说明

- 所有敏感信息通过环境变量配置
- 支持 HTTPS 健康检查
- 容器以非 root 用户运行
- 内置日志轮转和监控

## 📞 技术支持

如果遇到部署问题，请检查：

1. 环境变量是否正确配置
2. 网络连接是否正常
3. 容器日志中的错误信息
4. apply.build 平台的状态

## 📄 许可证

本项目基于 MIT 许可证开源。