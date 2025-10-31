# TG-Content-Bot-Pro 部署指南

## 📋 快速开始

### 1. 环境准备
```bash
# 克隆项目
git clone https://github.com/liwoyuandiane/TG-Content-Bot-Pro.git
cd TG-Content-Bot-Pro

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 复制配置文件
cp .env.example .env
```

### 2. 配置环境变量
编辑 `.env` 文件，填入以下必需配置：

```env
# Telegram API 配置
API_ID=your_api_id_here
API_HASH=your_api_hash_here
BOT_TOKEN=your_bot_token_here

# 机器人所有者
AUTH=your_user_id_here

# 数据库配置（可选）
MONGO_DB=mongodb://username:password@host:port/database
```

## 🚀 启动方式

### 前台运行（开发调试）
```bash
./start.sh
# 或
./start.sh --foreground
```

### 后台运行（生产环境）
```bash
./start.sh --background
```

### 进程管理
```bash
# 检查运行状态
./start.sh --status

# 停止运行
./start.sh --kill

# 重启
./start.sh --kill && ./start.sh --background
```

## 📊 监控和维护

### 查看日志
```bash
# 实时查看日志
tail -f logs/bot.log

# 查看最近100行日志
tail -n 100 logs/bot.log

# 搜索错误日志
grep "ERROR" logs/bot.log
```

### 系统资源监控
```bash
# 查看进程资源使用
top -p $(cat logs/bot.pid)

# 查看内存使用
ps -p $(cat logs/bot.pid) -o pid,ppid,cmd,%mem,%cpu --no-headers
```

## 🔧 高级配置

### 性能调优
在 `.env` 文件中添加以下可选配置：

```env
# 日志级别
LOG_LEVEL=INFO

# 加密密钥（增强安全性）
ENCRYPTION_KEY=your_32_char_encryption_key_here

# 代理配置（如果需要）
TELEGRAM_PROXY_HOST=proxy.example.com
TELEGRAM_PROXY_PORT=1080
TELEGRAM_PROXY_USERNAME=proxy_user
TELEGRAM_PROXY_PASSWORD=proxy_pass
```

### 数据库优化
确保 MongoDB 连接字符串正确：

```env
# MongoDB Atlas (云数据库)
MONGO_DB=mongodb+srv://username:password@cluster.mongodb.net/database

# 自建 MongoDB
MONGO_DB=mongodb://username:password@host:port/database?authSource=admin
```

## 🛠️ 故障排除

### 常见问题

**1. 启动失败：环境变量缺失**
```bash
# 检查配置
./start.sh --status

# 重新配置
cp .env.example .env
nano .env
```

**2. 数据库连接失败**
```bash
# 测试数据库连接
python3 -c "from pymongo import MongoClient; client = MongoClient('your_mongodb_uri'); client.admin.command('ping'); print('连接成功')"
```

**3. 内存使用过高**
```bash
# 重启进程释放内存
./start.sh --kill
./start.sh --background
```

**4. 查看详细错误信息**
```bash
# 查看完整错误日志
cat logs/bot.log | grep -A 10 -B 5 "ERROR"
```

### 性能优化建议

1. **定期重启**：建议每天自动重启一次，清理内存
2. **监控日志**：设置日志轮转，避免日志文件过大
3. **备份配置**：定期备份 `.env` 配置文件
4. **更新依赖**：定期更新 `requirements.txt` 中的依赖包

## 📈 监控指标

### 关键指标
- **正常运行时间**：检查进程状态
- **内存使用**：监控内存泄漏
- **错误率**：关注错误日志频率
- **响应时间**：监控API响应速度

### 健康检查
```bash
# 健康检查脚本
#!/bin/bash
if ./start.sh --status; then
    echo "✅ 服务正常"
    exit 0
else
    echo "❌ 服务异常"
    exit 1
fi
```

## 🔄 更新流程

### 常规更新
```bash
# 停止服务
./start.sh --kill

# 更新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt

# 重启服务
./start.sh --background
```

### 配置更新
```bash
# 备份当前配置
cp .env .env.backup

# 更新配置
nano .env

# 重启生效
./start.sh --kill && ./start.sh --background
```

## 📞 支持

如果遇到问题，请：
1. 检查日志文件 `logs/bot.log`
2. 确认环境变量配置正确
3. 查看本项目的问题页面

---

**版本**: 2.0.0  
**最后更新**: $(date +%Y-%m-%d)