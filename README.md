# TG消息提取器 (SaveRestrictedContentBot)

> Telegram 受限内容保存机器人 - 支持公开和私密频道消息克隆

一个功能强大的Telegram机器人，专门用于克隆和保存来自公开和私密频道的消息内容。支持流量监控、批量转发、自定义配置等功能。

## ✨ 核心特性

- ✅ 支持公开频道消息克隆
- ✅ 支持私密频道消息保存
- ✅ 流量监控和限制（每日/每月/累计统计）
- ✅ 批量转发（最多100条）
- ✅ 支持多种媒体类型转发
- ✅ 自适应速率限制
- ✅ 授权访问控制
- ✅ 全中文界面

## 🚀 快速开始

### 一键部署（推荐）

```bash
# 克隆项目
git clone https://github.com/liwoyuandiane/TG-Content-Bot-Pro.git
cd TG-Content-Bot-Pro

# 一键部署
chmod +x deploy.sh
./deploy.sh
```

或者使用远程脚本安装：
```bash
bash <(curl -sL https://raw.githubusercontent.com/liwoyuandiane/TG-Content-Bot-Pro/main/deploy.sh)
```

---

## 📋 环境变量配置

创建 `.env` 文件并配置以下变量：

```bash
# Telegram API凭证（必需）
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token

# 授权用户（必需）
AUTH=your_user_id

# MongoDB数据库（必需）
MONGO_DB=mongodb://localhost:27017/tg_content_bot

# 可选配置
SESSION=your_session_string
FORCESUB=channel_username
```

---

## 🐳 Docker部署

```bash
# 配置环境变量
cp .env.example .env
nano .env  # 编辑配置

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

---

## 🛠️ 部署方式

### 一键部署（推荐）

```bash
# 克隆项目
git clone https://github.com/liwoyuandiane/TG-Content-Bot-Pro.git
cd TG-Content-Bot-Pro

# 一键部署（自动检测环境并选择最优方式）
chmod +x deploy.sh
./deploy.sh
```

### Render平台部署

本项目已针对Render平台进行了优化，您可以轻松地将机器人部署到Render上：

1. 在Render上创建一个新的Web Service
2. 连接到您的GitHub仓库
3. 选择Docker环境进行部署
4. 在环境变量中配置以下必需的变量：
   - `API_ID`: 您的Telegram API ID
   - `API_HASH`: 您的Telegram API Hash
   - `BOT_TOKEN`: 您的Telegram Bot Token
   - `AUTH`: 您的Telegram用户ID（可以是单个ID或逗号分隔的多个ID）
   - `MONGO_DB`: MongoDB连接字符串

5. 部署时将使用项目中的Dockerfile进行构建
6. 健康检查端口已设置为8089，与应用配置一致

**注意事项**：
- Render平台免费套餐有512MB内存限制，请根据需要调整应用配置
- 建议使用外部MongoDB服务（如MongoDB Atlas）而不是Render提供的数据库
- 如果遇到连接问题，请检查Render的区域设置是否与您的代理配置兼容

**可选参数**：
```bash
# 强制使用Docker部署
./deploy.sh docker

# 强制使用手动部署
./deploy.sh manual

# 仅执行健康检查
./deploy.sh health

# 查看帮助
./deploy.sh --help
```

### Docker部署

```bash
# 克隆项目
git clone https://github.com/liwoyuandiane/TG-Content-Bot-Pro.git
cd TG-Content-Bot-Pro

# 配置环境变量
cp .env.example .env
nano .env  # 编辑配置

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 代理配置验证

您可以通过启动机器人来验证代理配置是否正确：

```bash
# 启动机器人测试代理配置
./start.sh
```

### 手动部署

```bash
# 克隆项目
git clone https://github.com/liwoyuandiane/TG-Content-Bot-Pro.git
cd TG-Content-Bot-Pro

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
nano .env  # 编辑配置

# 启动机器人
python3 -m main
```

### 代理配置

机器人支持 SOCKS5 和 HTTP 代理，以解决网络连接问题：

1. **SOCKS5 代理配置**：
   ```bash
   TELEGRAM_PROXY_SCHEME=socks5
   TELEGRAM_PROXY_HOST=154.201.86.151
   TELEGRAM_PROXY_PORT=38512
   TELEGRAM_PROXY_USERNAME=Ue9h0D55LS
   TELEGRAM_PROXY_PASSWORD=CaqlJmzRWc
   ```

2. **HTTP 代理配置**：
   ```bash
   TELEGRAM_PROXY_SCHEME=http
   TELEGRAM_PROXY_HOST=154.201.86.151
   TELEGRAM_PROXY_PORT=19496
   TELEGRAM_PROXY_USERNAME=wCBcuVZXd6
   TELEGRAM_PROXY_PASSWORD=XM1Xdwey02
   ```

3. **Cloudflare Workers Telegram API 代理**：
   如果您的服务器无法直接连接到 Telegram API，可以部署 Cloudflare Workers 作为代理：
   
   - 部署 `cloudflare-worker.js` 到 Cloudflare Workers
   - 在 `.env` 文件中配置：
   ```bash
   TELEGRAM_API_PROXY_URL=https://your-worker.your-account.workers.dev
   ```
   
   详细配置说明请参考项目文档。

详细配置说明请参考项目文档。

---

## 📖 使用说明

### 基本命令

- `/start` - 初始化机器人，显示个人统计
- `/batch` - 批量转发消息（仅所有者，最多100条）
- `/cancel` - 取消正在进行的批量操作（仅所有者）
- `/traffic` - 查看个人流量统计
- `/stats` - 查看机器人统计（仅所有者）
- `/history` - 查看转发记录（仅所有者）
- `/queue` - 查看队列状态（仅所有者）
- `/totaltraffic` - 查看总流量统计（仅所有者）
- `/setlimit` - 配置流量限制（仅所有者）
- `/resettraffic` - 重置流量统计（仅所有者）
- `/addsession` - 添加用户SESSION（仅所有者）
- `/delsession` - 删除用户SESSION（仅所有者）
- `/sessions` - 列出所有存储的SESSION（仅所有者）
- `/mysession` - 查看自己的SESSION字符串
- `/clearhistory` - 清除转发历史（仅所有者）

### 消息转发

1. 发送任意消息链接到机器人
2. 机器人会自动转发给您

支持的消息链接格式：
- 公开频道：`https://t.me/channelname/messageid`
- 私密频道：`https://t.me/c/chatid/messageid`

---

## 📄 许可证

本项目基于MIT许可证开源。