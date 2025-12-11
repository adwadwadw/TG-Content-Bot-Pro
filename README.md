# TG消息提取器 (SaveRestrictedContentBot)

> Telegram 受限内容保存机器人 - 支持公开和私密频道消息克隆

一个功能强大的Telegram机器人，专门用于克隆和保存来自公开和私密频道的消息内容。支持流量监控、批量下载、自定义配置等功能，具备完善的错误处理和自适应速率限制机制。

[![GitHub stars](https://img.shields.io/github/stars/liwoyuandiane/TG-Content-Bot-Pro?style=social)](https://github.com/liwoyuandiane/TG-Content-Bot-Pro)
[![License](https://img.shields.io/github/license/liwoyuandiane/TG-Content-Bot-Pro)](LICENSE)

## ✨ 特性

- ✅ 支持公开频道消息克隆
- ✅ 支持私密频道消息保存
- ✅ 流量监控和限制（每日/每月/累计统计）
- ✅ 自定义缩略图
- ✅ 批量下载（最多100条）
- ✅ 支持文本、图片、视频、文件
- ✅ 自适应速率限制
- ✅ 强制订阅功能
- ✅ 全中文界面
- ✅ 在线生成 SESSION
- ✅ 授权访问控制

## 🚀 快速开始

### Docker部署（推荐）

请参考下面的Docker部署部分进行安装。

### 手动部署

请参考下面的手动部署部分进行安装。

**安装完成后**：
```bash
cd ~/TG-Content-Bot-Pro
./start.sh
```

---

## 📋 环境变量

| 变量名 | 说明 | 获取方式 | 必需 |
|--------|------|---------|------|
| API_ID | Telegram API ID | [my.telegram.org](https://my.telegram.org) | ✅ |
| API_HASH | Telegram API Hash | [my.telegram.org](https://my.telegram.org) | ✅ |
| BOT_TOKEN | 机器人Token | [@BotFather](https://t.me/BotFather) | ✅ |
| AUTH | 授权用户ID | [@userinfobot](https://t.me/userinfobot) | ✅ |
| MONGO_DB | MongoDB连接字符串 | [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) | ✅ |
| SESSION | Pyrogram会话字符串 | 手动生成或使用Telegram应用生成 | ❌ |
| FORCESUB | 强制订阅频道 | 频道用户名（不带@） | ❌ |
| TELEGRAM_PROXY_SCHEME | Telegram代理协议 | socks5或http | ❌ |
| TELEGRAM_PROXY_HOST | Telegram代理主机 | 代理服务器地址 | ❌ |
| TELEGRAM_PROXY_PORT | Telegram代理端口 | 代理服务器端口 | ❌ |
| TELEGRAM_PROXY_USERNAME | Telegram代理用户名 | 代理认证用户名 | ❌ |
| TELEGRAM_PROXY_PASSWORD | Telegram代理密码 | 代理认证密码 | ❌ |

---

## 🌿 分支策略（GitHub Actions自动构建）

本项目采用双分支策略，实现自动构建与快速部署的分离：

### 分支说明

#### main分支（开发分支）
- **用途**：代码开发和镜像构建
- **Dockerfile**：完整的构建流程（从python:3.11-slim开始）
- **GitHub Actions**：自动构建并推送到GitHub Container Registry
- **文件结构**：包含完整的源代码和构建配置

#### pull分支（部署分支）
- **用途**：极简部署，无需重新构建
- **Dockerfile**：直接使用构建好的镜像（FROM ghcr.io/liwoyuandiane/tg-content-bot-pro:main）
- **文件结构**：仅包含部署所需的最少文件（4个文件）
- **极简设计**：Dockerfile只有一行，专注于快速部署

### GitHub Actions多架构构建

项目支持多架构镜像构建：
- **支持的架构**：linux/amd64, linux/arm64
- **镜像标签**：
  - `ghcr.io/liwoyuandiane/tg-content-bot-pro:main` - 主分支镜像
  - `ghcr.io/liwoyuandiane/tg-content-bot-pro:latest` - 最新稳定版
- **健康检查**：内置HTTP健康检查端点（端口8080）

### 工作流程

1. **开发阶段（main分支）**：
   ```bash
   git checkout main
   # 进行代码修改
   git add .
   git commit -m "功能更新"
   git push origin main
   # GitHub Actions会自动构建多架构镜像
   ```

2. **部署阶段（pull分支）**：
   ```bash
   git checkout pull
   cp .env.example .env
   nano .env  # 配置环境变量
   docker-compose up -d  # 直接使用预构建的镜像，部署更快
   ```

3. **健康检查**：
   ```bash
   # 检查应用状态
   curl http://localhost:8080/health
   # 查看状态页面
   curl http://localhost:8080/
   ```

### 极简部署优势

- 🚀 **快速部署**：pull分支只有4个文件，下载秒完成
- 🏗️ **多架构支持**：支持x86和ARM架构的服务器
- 🔍 **健康监控**：内置HTTP健康检查，便于容器编排
- 📦 **版本控制**：GitHub Actions自动管理镜像版本
- 🔒 **安全可靠**：使用GitHub官方容器注册表

### 文件结构对比

**main分支（开发构建）**：
```
├── main/           # 源代码目录
├── scripts/        # 构建脚本
├── .github/        # GitHub Actions配置
├── Dockerfile      # 完整构建流程
└── docker-compose.yml
```

**pull分支（极简部署）**：
```
├── Dockerfile      # 只有一行：FROM ghcr.io/liwoyuandiane/tg-content-bot-pro:main
├── docker-compose.yml
├── .env.example    # 环境变量模板
└── README.md       # 使用说明
```

---

## 🛠️ 部署方式

### Docker部署（推荐）

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
- `/batch` - 批量下载消息（仅所有者，最多100条）
- `/cancel` - 取消正在进行的批量操作（仅所有者）
- `/traffic` - 查看个人流量统计（每日/每月/累计）
- `/stats` - 查看机器人统计（仅所有者）
- `/history` - 查看最近20次下载记录（仅所有者）
- `/queue` - 查看队列和速率限制状态（仅所有者）
- `/totaltraffic` - 查看总流量统计（仅所有者）
- `/setlimit` - 配置流量限制（仅所有者）
- `/resettraffic` - 重置流量统计（仅所有者）
- `/addsession` - 添加用户SESSION（仅所有者）
- `/delsession` - 删除用户SESSION（仅所有者）
- `/sessions` - 列出所有存储的SESSION（仅所有者）
- `/mysession` - 查看自己的SESSION字符串

### 消息克隆

1. 发送任意消息链接到机器人
2. 机器人会自动下载并发送给您

支持的消息链接格式：
- 公开频道：`https://t.me/channelname/messageid`
- 私密频道：`https://t.me/c/chatid/messageid`
- 机器人频道：`https://t.me/b/chatid/messageid`

### 批量下载

1. 发送`/batch`命令
2. 按提示发送起始消息链接
3. 按提示发送要下载的消息数量（最多100条）

---

## 🔧 技术架构

### 三客户端系统

机器人同时运行三个Telegram客户端：

1. **bot** (Telethon) - 主机器人客户端，用于事件处理和大文件上传
2. **userbot** (Pyrogram) - 用户会话客户端，用于访问受限频道
3. **Bot** (Pyrogram) - 辅助机器人客户端，用于Pyrogram特定操作

### 插件系统

插件自动从`main/plugins/`目录加载：
- `main/__main__.py`使用glob发现所有`.py`文件
- `main/utils.py:load_plugins()`动态导入每个插件
- 插件使用Telethon/Pyrogram的装饰器注册事件处理器

### 核心消息流程

1. 用户发送消息链接 → `frontend.py`或`start.py`处理请求
2. 链接解析 → `helpers.py:get_link()`提取chat_id和msg_id
3. 消息获取 → `pyroplug.py:get_msg()`从源频道下载
4. 流量检查 → `database.py:check_traffic_limit()`验证用户配额
5. 上传给用户 → 根据媒体类型/大小使用Pyrogram或Telethon
6. 清理 → 下载的文件在上传后被删除

### 文件上传策略 (`pyroplug.py:get_msg()`)

实现回退逻辑：
- 首先尝试Pyrogram上传
- 失败时回退到Telethon的`fast_upload`处理大文件或错误
- 针对视频笔记、视频、照片、文档的不同处理
- 使用ethon库自动提取元数据

### 数据库系统

**MongoDB数据库** (`main/database.py`) - 所有数据存储必需：
- **users**: user_id, username, is_banned, join_date, last_used
- **download_history**: message_id, chat_id, media_type, file_size, status
- **user_stats**: total_downloads, total_size per user
- **batch_tasks**: 批量操作进度跟踪
- **user_traffic**: 每日/每月/累计上传/下载统计
- **traffic_limits**: 全局流量限制配置
- **settings**: 流量限制配置

### 任务队列和速率限制 (`main/queue_manager.py`)

三组件系统：
1. **TaskQueue**: 异步队列，3个并发工作者处理并行任务
2. **RateLimiter**: 令牌桶算法实现平滑速率控制
3. **AdaptiveRateLimiter**: 根据Telegram响应自动调整速率
   - 初始速率：0.5请求/秒
   - 范围：0.1 - 10请求/秒
   - 突发：3个令牌
   - 遇到FloodWait：速率降低50%
   - 连续10次成功后：速率提高20%

---

## 📊 流量管理

默认限制（可通过`/setlimit`命令配置）：
- 每日限制：1GB/用户
- 每月限制：10GB/用户
- 单文件限制：100MB
- 默认启用

流量在每次下载前检查：
- 从消息元数据获取文件大小
- 调用`db.check_traffic_limit(sender, file_size)`
- 超过配额时拒绝下载并显示信息
- 成功上传后记录流量

---

## 🛡️ 安全特性

- SESSION字符串加密存储（可选）
- 用户访问控制（仅授权用户可使用）
- 流量限制防止滥用
- 自适应速率限制避免被Telegram限制
- 错误处理和日志记录

---

## 📈 性能优化

- 异步处理提高并发能力
- 自适应速率限制优化请求频率
- 连接池管理减少资源消耗
- 内存优化避免内存泄漏
- 批量下载提高效率

---

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

---

## 📄 许可证

本项目基于MIT许可证开源。