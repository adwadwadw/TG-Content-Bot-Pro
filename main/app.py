"""应用主入口"""
import sys
import logging
import asyncio
import glob
import os
import threading
import atexit
import fcntl
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from pyrogram.types import BotCommand

from .core.clients import client_manager
from .core.database import db_manager
from .core.plugin_manager import plugin_manager
from .utils.logging_config import setup_logging, get_logger
from .config import settings

# 设置日志
setup_logging()
logger = get_logger(__name__)

# 单实例锁文件
LOCK_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".app.lock")
lock_file = None


# 健康检查处理器
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body><h1>TG Content Bot Pro</h1><p>Status: Running</p><p><a href="/health">Health Check</a></p></body></html>')
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        # 重写日志方法，避免打印到控制台
        pass


def acquire_lock():
    """获取单实例锁"""
    global lock_file
    try:
        # 检查锁文件是否已存在
        if os.path.exists(LOCK_FILE_PATH):
            # 尝试读取现有锁文件中的PID
            try:
                with open(LOCK_FILE_PATH, 'r') as f:
                    existing_pid = f.read().strip()
                    if existing_pid:
                        # 检查该进程是否仍在运行
                        try:
                            os.kill(int(existing_pid), 0)  # 不发送信号，只检查进程是否存在
                            logger.error(f"❌ 检测到另一个实例正在运行 (PID: {existing_pid})，无法启动多个实例")
                            return False
                        except (OSError, ValueError):
                            # 进程不存在，可以安全地覆盖锁文件
                            logger.warning(f"⚠️  检测到陈旧的锁文件 (PID: {existing_pid} 已不存在)，将重新创建锁")
            except Exception as e:
                logger.warning(f"⚠️  读取现有锁文件时出错: {e}，将重新创建锁")
        
        # 创建锁文件
        lock_file = open(LOCK_FILE_PATH, 'w')
        # 尝试获取独占锁
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        # 写入进程ID
        lock_file.write(str(os.getpid()))
        lock_file.flush()
        logger.info("✅ 成功获取单实例锁")
        return True
    except IOError:
        logger.error("❌ 无法获取单实例锁，可能已有另一个实例在运行")
        if lock_file:
            lock_file.close()
            lock_file = None
        return False

def release_lock():
    """释放单实例锁"""
    global lock_file
    if lock_file:
        try:
            # 删除锁文件
            os.unlink(LOCK_FILE_PATH)
            lock_file.close()
            logger.info("🔒 单实例锁已释放")
        except Exception as e:
            logger.error(f"❌ 释放单实例锁时出错: {e}")
        finally:
            lock_file = None

def start_health_server():
    """启动健康检查HTTP服务器"""
    port = int(os.getenv('HEALTH_CHECK_PORT', '8089'))
    try:
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        logger.info(f"✅ 健康检查服务器已启动，端口: {port}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"❌ 启动健康检查服务器失败: {e}")
        # 如果端口被占用，尝试使用备用端口
        try:
            server = HTTPServer(('0.0.0.0', 8081), HealthCheckHandler)
            logger.info(f"✅ 健康检查服务器已启动，备用端口: 8081")
            server.serve_forever()
        except Exception as e2:
            logger.error(f"❌ 启动备用端口健康检查服务器失败: {e2}")


def check_and_reset_database():
    """检查并重置数据库（如果DB_RESET环境变量为true）"""
    db_reset = os.environ.get('DB_RESET', '').lower() in ['true', '1', 'yes']
    
    if db_reset:
        logger.info("🔄 检测到 DB_RESET=true，开始重置数据库...")
        
        try:
            if not db_manager.is_connected():
                logger.error("❌ 数据库未连接，无法执行重置")
                return False
                
            # 删除所有集合中的数据
            collections = ["users", "message_history", "batch_tasks", "settings"]
            for collection_name in collections:
                if collection_name in db_manager.db.list_collection_names():
                    count = db_manager.db[collection_name].count_documents({})
                    db_manager.db[collection_name].delete_many({})
                    logger.info(f"  ✅ 清空集合 {collection_name} ({count} 条记录)")
            
            # 重新创建必要的索引
            logger.info("  🔄 重新创建索引...")
            db_manager._create_indexes()
            
            # 添加主用户
            auth_users = settings.get_auth_users()
            for user_id in auth_users:
                db_manager.db.users.insert_one({
                    "user_id": user_id,
                    "is_authorized": True,
                    "is_banned": False,
                    "join_date": datetime.now(),
                    "total_forwards": 0,
                    "total_size": 0,
                    "daily_upload": 0,
                    "daily_download": 0,
                    "monthly_upload": 0,
                    "monthly_download": 0,
                    "total_upload": 0,
                    "total_download": 0,
                    "last_reset_daily": datetime.now().date().isoformat(),
                    "last_reset_monthly": datetime.now().strftime("%Y-%m")
                })
                logger.info(f"  ✅ 添加主用户 {user_id}")
            
            logger.info("✅ 数据库重置完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 数据库重置过程中出错: {e}")
            return False


async def setup_commands():
    """设置机器人命令"""
    commands = [
        BotCommand("start", "🚀 开始使用机器人"),
        BotCommand("help", "📖 显示帮助信息"),
        BotCommand("batch", "📦 批量保存消息（仅所有者）"),
        BotCommand("cancel", "❌ 取消批量任务（仅所有者）"),
        BotCommand("stats", "📊 查看统计信息（仅所有者）"),
        BotCommand("history", "📜 查看转发历史（仅所有者）"),
        BotCommand("queue", "📋 查看队列状态（仅所有者）"),
        BotCommand("traffic", "📊 查看流量统计"),
        BotCommand("totaltraffic", "🌐 查看总流量（仅所有者）"),
        BotCommand("setlimit", "⚙️ 设置流量限制（仅所有者）"),
        BotCommand("resettraffic", "🔄 重置流量统计（仅所有者）"),
        BotCommand("clearhistory", "🗑️ 清除转发历史（仅所有者）"),
        BotCommand("addsession", "➕ 添加SESSION（仅所有者）"),
        BotCommand("generatesession", "🔐 在线生成SESSION（仅所有者）"),
        BotCommand("cancelsession", "🚫 取消SESSION生成（仅所有者）"),
        BotCommand("delsession", "➖ 删除SESSION（仅所有者）"),
        BotCommand("sessions", "📋 查看所有SESSION（仅所有者）"),
        BotCommand("mysession", "🔐 查看我的SESSION")
    ]
    
    try:
        await client_manager.pyrogram_bot.set_bot_commands(commands)
        logger.info("机器人命令已自动设置完成！")
    except Exception as e:
        logger.error(f"设置命令时出错: {e}", exc_info=True)


async def load_all_plugins():
    """加载所有插件"""
    try:
        from .core.base_plugin import plugin_registry
        
        results = plugin_manager.load_all_plugins()
        loaded_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        logger.info(f"插件加载完成: {loaded_count}/{total_count} 个插件加载成功")
        
        # 记录加载失败的插件
        failed_plugins = [name for name, success in results.items() if not success]
        if failed_plugins:
            logger.warning(f"以下插件加载失败: {', '.join(failed_plugins)}")
        
        # 调用所有插件的on_load()方法来注册事件处理器
        await plugin_registry.load_all_plugins()
        logger.info(f"插件事件处理器已注册")
    except Exception as e:
        logger.error(f"加载插件时出错: {e}", exc_info=True)


async def startup():
    """应用启动"""
    logger.info("=" * 50)
    logger.info("🤖 TG-Content-Bot-Pro 启动中...")
    logger.info("=" * 50)
    
    # 检查并重置数据库（如果需要）
    check_and_reset_database()
    
    # 配置验证
    try:
        from .utils.config_validator import ensure_config_integrity
        config_valid = ensure_config_integrity()
        if not config_valid:
            logger.warning("⚠️ 配置验证失败，应用将以降级模式启动")
            logger.warning("📡 仅启动健康检查服务，无法连接到Telegram")
            logger.warning("💡 请检查.env文件中的API_ID、API_HASH和BOT_TOKEN配置")
            
            # 降级模式：只启动健康检查服务
            return False
    except Exception as e:
        logger.error(f"配置验证时出错: {e}", exc_info=True)
        logger.warning("应用将以降级模式启动")
        return False
    
    # 初始化客户端
    try:
        await client_manager.initialize_clients()
        logger.info(f"客户端初始化成功，bot实例: {client_manager.bot}")
    except Exception as e:
        logger.error(f"客户端初始化失败: {e}", exc_info=True)
        logger.warning("将继续启动应用，但部分功能可能不可用")
    
    # 启动任务队列（已移除下载功能，跳过任务队列初始化）
    logger.info("ℹ️  已移除下载功能，跳过任务队列初始化")
    
    # 加载插件
    await load_all_plugins()
    
    # 检查事件处理器
    if client_manager.bot:
        handlers = list(client_manager.bot.list_event_handlers())
        logger.info(f"✅ Telethon注册的事件处理器数量: {len(handlers)}")
        for i, (handler, event) in enumerate(handlers):
            logger.info(f"  {i+1}. {handler.__name__}")
    else:
        logger.error("❌ Bot客户端未初始化！")
    
    # 设置机器人命令（确保客户端已启动）
    try:
        if client_manager.pyrogram_bot and client_manager.pyrogram_bot.is_connected:
            await setup_commands()
        else:
            logger.warning("Pyrogram客户端未连接，跳过命令设置")
    except Exception as e:
        logger.error(f"设置机器人命令失败: {e}", exc_info=True)
        logger.warning("机器人命令设置失败，但应用将继续运行")
    
    logger.info("✅ 部署成功！")
    logger.info("📱 TG消息提取器已启动")
    logger.info("🗄️  数据库初始化完成")
    logger.info("🤖 机器人命令已自动同步...")
    logger.info("=" * 50)


async def shutdown():
    """应用关闭"""
    logger.info("正在关闭应用...")
    
    # 停止任务队列（已移除下载功能，跳过任务队列停止）
    logger.info("ℹ️  已移除下载功能，跳过任务队列停止")
    
    # 停止客户端
    await client_manager.stop_clients()
    logger.info("应用已关闭")


async def main_async():
    """异步主函数"""
    try:
        # 运行启动函数
        startup_result = await startup()
        
        # 如果启动失败（配置无效），进入降级模式
        if startup_result is False:
            logger.info("📡 降级模式启动完成 - 仅健康检查服务可用")
            logger.info("🔗 健康检查地址: http://localhost:8089/health")
            logger.info("💡 请配置有效的Telegram API凭证以启用完整功能")
            
            # 保持应用运行，提供健康检查服务
            try:
                while True:
                    await asyncio.sleep(60)  # 每分钟检查一次
                    logger.debug("降级模式运行中...")
            except KeyboardInterrupt:
                logger.info("收到中断信号，正在关闭...")
            return
        
        # 检查客户端是否已初始化
        if client_manager.bot is not None and hasattr(client_manager.bot, 'is_connected') and client_manager.bot.is_connected():
            logger.info("🚀 机器人开始监听消息...")
            # 运行主客户端直到断开连接
            await client_manager.bot.run_until_disconnected()
        else:
            logger.warning("⚠️ 客户端未初始化或未连接，机器人将以降级模式运行...")
            logger.info("📡 健康检查服务器已启动，可以访问 http://localhost:8089/health 检查服务状态")
            logger.info("⏰ 应用将保持运行，等待客户端连接...")
            
            # 保持应用运行，即使客户端未连接
            try:
                while True:
                    await asyncio.sleep(60)  # 每分钟检查一次
                    logger.debug("应用仍在运行...")
            except KeyboardInterrupt:
                logger.info("收到中断信号，正在关闭...")
            
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭...")
    except Exception as e:
        logger.error(f"应用运行时出错: {e}", exc_info=True)
    finally:
        # 确保正确关闭
        await shutdown()


def main():
    """主函数"""
    # 检查是否能获取单实例锁
    if not acquire_lock():
        logger.error("🚨 程序已在运行中，无法启动多个实例")
        logger.info("💡 如需启动新实例，请先停止当前运行的实例")
        sys.exit(1)
    
    # 注册退出处理函数，确保程序退出时释放锁
    atexit.register(release_lock)
    
    # 在后台启动健康检查服务器
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    try:
        # 使用单个事件循环运行整个应用
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("收到中断信号")
    except Exception as e:
        logger.error(f"主函数出错: {e}", exc_info=True)
    finally:
        # 确保释放锁
        release_lock()


if __name__ == "__main__":
    main()