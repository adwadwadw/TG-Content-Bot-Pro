"""帮助命令插件"""
import logging
from telethon import events

from ..core.base_plugin import BasePlugin
from ..core.clients import client_manager
from ..services.user_service import user_service
from ..services.permission_service import permission_service

logger = logging.getLogger(__name__)


class HelpPlugin(BasePlugin):
    """帮助命令插件"""
    
    def __init__(self):
        super().__init__("help")
        self.drone = client_manager.bot
    
    async def on_load(self):
        """插件加载时注册事件处理器"""
        # 重新获取bot实例（确保是最新的）
        self.drone = client_manager.bot
        
        if self.drone is None:
            logger.error("Bot客户端未初始化，无法注册事件处理器")
            return
        
        # 注册消息处理器
        self.drone.add_event_handler(self.help_command, events.NewMessage(incoming=True, pattern="/help"))
        
        logger.info(f"帮助插件事件处理器已注册")
    
    async def on_unload(self):
        """插件卸载时移除事件处理器"""
        # 移除事件处理器
        self.drone.remove_event_handler(self.help_command, events.NewMessage(incoming=True, pattern="/help"))
        
        logger.info("帮助插件事件处理器已移除")
    
    async def help_command(self, event):
        """处理 /help 命令"""
        from ..config import settings
        
        user_id = event.sender_id
        
        logger.info(f"收到 /help 命令，用户ID: {user_id}")
        
        # 只允许授权用户使用
        if not await permission_service.require_authorized(user_id):
            logger.warning(f"未授权用户尝试使用帮助命令: {user_id}")
            await event.reply("❌ 您没有权限使用此机器人")
            return
        
        # 检查用户是否被封禁
        if await user_service.is_user_banned(user_id):
            await event.reply("您已被封禁，无法使用此机器人。")
            return
        
        help_text = """🤖 **TG-Content-Bot-Pro 使用帮助**

📋 **核心功能**
• 发送任意消息链接即可克隆内容到这里
• 支持私密频道消息（需先发送邀请链接）
• 批量转发消息内容
• 文件转发和自动管理

🛠️ **主要命令列表**

**基础命令**
`/start` - 🚀 开始使用机器人
`/help` - 📖 显示此帮助信息

**转发管理**
`/batch` - 📦 批量保存消息（仅所有者）
`/cancel` - ❌ 取消批量任务（仅所有者）
`/queue` - 📋 查看队列状态（仅所有者）

**统计信息**
`/stats` - 📊 查看统计信息（仅所有者）
`/history` - 📜 查看转发历史（仅所有者）
`/traffic` - 📊 查看流量统计
`/totaltraffic` - 🌐 查看总流量（仅所有者）

**流量控制**
`/setlimit` - ⚙️ 设置流量限制（仅所有者）
`/resettraffic` - 🔄 重置流量统计（仅所有者）
`/clearhistory` - 🗑️ 清除转发历史（仅所有者）

**SESSION管理**
`/addsession` - ➕ 添加SESSION（仅所有者）
`/generatesession` - 🔐 在线生成SESSION（仅所有者）
`/cancelsession` - 🚫 取消SESSION生成（仅所有者）
`/delsession` - ➖ 删除SESSION（仅所有者）
`/sessions` - 📋 查看所有SESSION（仅所有者）
`/mysession` - 🔐 查看我的SESSION

⚡ **使用提示**
1. 发送消息链接时，确保机器人有相应的访问权限
2. 私密频道需要先发送邀请链接给机器人
3. 批量转发功能仅限所有者使用
4. 流量统计帮助您监控转发用量

🔧 **技术支持**
如有问题或建议，请联系开发者: @tgxxtq

**版本信息**
TG-Content-Bot-Pro - 专业的Telegram内容下载工具
"""
        
        await event.reply(help_text)
        logger.info(f"帮助信息已发送给用户 {user_id}")


# 创建插件实例并注册
help_plugin = HelpPlugin()

# 注册到插件注册表
from ..core.base_plugin import plugin_registry
plugin_registry.register(help_plugin)