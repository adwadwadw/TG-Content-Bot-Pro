"""下载命令插件

提供多平台视频和音频下载功能，支持 YouTube、Instagram、Facebook 等平台。
"""
import asyncio
import logging
import os
from typing import Optional

from telethon import events
from telethon.tl.custom import Message
from pyrogram import filters

from ..core.base_plugin import BasePlugin
from ..core.base_plugin import plugin_registry as _plugin_registry
from ..core.clients import client_manager
from ..services.download_service import download_service
from ..services.traffic_service import traffic_service
from ..utils.permission_decorators import require_owner
from ..config import settings
from ..exceptions.telegram import DownloadFailedException

logger = logging.getLogger(__name__)


class DownloadCommands(BasePlugin):
    """下载命令插件"""
    
    def __init__(self):
        """初始化插件"""
        super().__init__("download_commands")
        self.telethon_client = client_manager.bot
        self.pyrogram_client = client_manager.pyrogram_bot
    
    async def on_load(self):
        """加载插件"""
        logger.info("加载下载命令插件")
        
        # 注册 Telethon 命令
        if self.telethon_client:
            self.telethon_client.add_event_handler(
                self.handle_dl_command,
                events.NewMessage(pattern=r'/dl(?:\s+(.*))?$')
            )
            
            self.telethon_client.add_event_handler(
                self.handle_adl_command,
                events.NewMessage(pattern=r'/adl(?:\s+(.*))?$')
            )
        
        # 注册 Pyrogram 命令
        if self.pyrogram_client:
            @self.pyrogram_client.on_message(filters.command("dl", prefixes=["/"]) & filters.private)
            async def pyro_dl_command(client, message):
                await self.handle_pyro_dl_command(client, message)
            
            @self.pyrogram_client.on_message(filters.command("adl", prefixes=["/"]) & filters.private)
            async def pyro_adl_command(client, message):
                await self.handle_pyro_adl_command(client, message)
    
    async def handle_dl_command(self, event: events.NewMessage.Event):
        """处理 Telethon 的 /dl 命令（视频下载）"""
        logger.info(f"收到 /dl 命令，用户 ID: {event.sender_id}")
        await self._handle_download_command(event, is_audio=False)
    
    async def handle_adl_command(self, event: events.NewMessage.Event):
        """处理 Telethon 的 /adl 命令（音频下载）"""
        logger.info(f"收到 /adl 命令，用户 ID: {event.sender_id}")
        await self._handle_download_command(event, is_audio=True)
    
    async def handle_pyro_dl_command(self, client, message):
        """处理 Pyrogram 的 /dl 命令（视频下载）"""
        logger.info(f"Pyrogram 收到 /dl 命令，用户 ID: {message.from_user.id}")
        await self._handle_pyro_download_command(client, message, is_audio=False)
    
    async def handle_pyro_adl_command(self, client, message):
        """处理 Pyrogram 的 /adl 命令（音频下载）"""
        logger.info(f"Pyrogram 收到 /adl 命令，用户 ID: {message.from_user.id}")
        await self._handle_pyro_download_command(client, message, is_audio=True)
    
    async def _handle_download_command(self, event: events.NewMessage.Event, is_audio: bool = False):
        """处理 Telethon 下载命令
        
        Args:
            event: 事件对象
            is_audio: 是否为音频下载
        """
        try:
            # 解析命令参数
            args = event.pattern_match.group(1)
            if not args:
                await event.reply("请提供要下载的视频链接，格式: /dl <视频链接>")
                return
            
            url = args.strip()
            
            # 发送正在处理的消息
            processing_msg = await event.reply(f"{'正在下载音频...' if is_audio else '正在下载视频...'}")
            
            # 定义进度回调函数
            async def progress_callback(data):
                if data['status'] == 'downloading':
                    # 更新进度信息
                    await processing_msg.edit(f"{'下载音频' if is_audio else '下载视频'}中...\n"\
                                           f"进度: {data['percent']}\n"\
                                           f"速度: {data['speed']}\n"\
                                           f"剩余时间: {data['eta']}")
                elif data['status'] == 'finished':
                    # 下载完成，更新消息
                    await processing_msg.edit(f"{'音频' if is_audio else '视频'}下载完成，正在上传...")
            
            # 获取用户ID
            user_id = event.sender_id
            
            # 执行下载
            if is_audio:
                file_path, title, file_size = await download_service.download_audio(url, progress_callback=progress_callback)
                
                # 检查流量限制
                if not await traffic_service.check_user_traffic(user_id, file_size):
                    await event.reply("流量不足，无法下载")
                    download_service.cleanup(file_path)
                    return
                
                # 发送音频文件
                await event.reply(file=file_path, caption=title)
            else:
                file_path, title, file_size, duration = await download_service.download_video(url, progress_callback=progress_callback)
                
                # 检查流量限制
                if not await traffic_service.check_user_traffic(user_id, file_size):
                    await event.reply("流量不足，无法下载")
                    download_service.cleanup(file_path)
                    return
                
                # 生成视频截图
                screenshot_path = None
                if duration > 0:
                    from ..utils.video_processor import video_processor
                    await processing_msg.edit("正在生成视频截图...")
                    screenshot_path = await video_processor.screenshot(file_path, int(duration), str(user_id))
                
                # 发送视频文件
                from ..utils.file_manager import file_manager
                
                # 检查文件大小，如果超过限制则分片上传
                CHUNK_SIZE = 1900 * 1024 * 1024  # 1.9GB，Telegram上传限制
                if os.path.getsize(file_path) > CHUNK_SIZE:
                    # 分割文件
                    chunks = file_manager.split_file(file_path, CHUNK_SIZE)
                    
                    # 发送所有分片
                    for i, chunk_file in enumerate(chunks):
                        chunk_caption = f"{title}\n\n**分片 {i+1}/{len(chunks)}**"
                        await event.reply(
                            file=chunk_file, 
                            caption=chunk_caption,
                            thumb=screenshot_path if screenshot_path else None
                        )
                    
                    # 清理分片文件
                    for chunk_file in chunks:
                        if chunk_file != file_path and os.path.exists(chunk_file):
                            file_manager.safe_remove(chunk_file)
                else:
                    # 直接发送文件
                    await event.reply(
                        file=file_path, 
                        caption=title,
                        thumb=screenshot_path if screenshot_path else None
                    )
                
                # 清理截图文件
                if screenshot_path and os.path.exists(screenshot_path):
                    os.remove(screenshot_path)
            
            # 更新流量统计
            await traffic_service.update_user_traffic(user_id, file_size)
            
            # 清理临时文件
            download_service.cleanup(file_path)
            
            # 删除处理中的消息
            await processing_msg.delete()
            
        except DownloadFailedException as e:
            await event.reply(f"下载失败: {e}")
        except Exception as e:
            logger.error(f"处理下载命令时出错: {e}")
            await event.reply(f"处理命令时出错: {e}")
    
    async def _handle_pyro_download_command(self, client, message, is_audio: bool = False):
        """处理 Pyrogram 下载命令
        
        Args:
            client: Pyrogram 客户端
            message: 消息对象
            is_audio: 是否为音频下载
        """
        try:
            # 解析命令参数
            if len(message.command) < 2:
                await message.reply("请提供要下载的视频链接，格式: /dl <视频链接>")
                return
            
            url = message.command[1]
            
            # 发送正在处理的消息
            processing_msg = await message.reply(f"{'正在下载音频...' if is_audio else '正在下载视频...'}")
            
            # 定义进度回调函数
            async def progress_callback(data):
                if data['status'] == 'downloading':
                    # 更新进度信息
                    await processing_msg.edit(f"{'下载音频' if is_audio else '下载视频'}中...\n"\
                                           f"进度: {data['percent']}\n"\
                                           f"速度: {data['speed']}\n"\
                                           f"剩余时间: {data['eta']}")
                elif data['status'] == 'finished':
                    # 下载完成，更新消息
                    await processing_msg.edit(f"{'音频' if is_audio else '视频'}下载完成，正在上传...")
            
            # 获取用户ID
            user_id = message.from_user.id
            
            # 执行下载
            if is_audio:
                file_path, title, file_size = await download_service.download_audio(url, progress_callback=progress_callback)
                
                # 检查流量限制
                if not await traffic_service.check_user_traffic(user_id, file_size):
                    await message.reply("流量不足，无法下载")
                    download_service.cleanup(file_path)
                    return
                
                # 发送音频文件
                await client.send_document(
                    chat_id=message.chat.id,
                    document=file_path,
                    caption=title
                )
            else:
                file_path, title, file_size, duration = await download_service.download_video(url, progress_callback=progress_callback)
                
                # 检查流量限制
                if not await traffic_service.check_user_traffic(user_id, file_size):
                    await message.reply("流量不足，无法下载")
                    download_service.cleanup(file_path)
                    return
                
                # 生成视频截图
                screenshot_path = None
                if duration > 0:
                    from ..utils.video_processor import video_processor
                    await processing_msg.edit("正在生成视频截图...")
                    screenshot_path = await video_processor.screenshot(file_path, int(duration), str(user_id))
                
                # 发送视频文件
                from ..utils.file_manager import file_manager
                
                # 检查文件大小，如果超过限制则分片上传
                CHUNK_SIZE = 1900 * 1024 * 1024  # 1.9GB，Telegram上传限制
                if os.path.getsize(file_path) > CHUNK_SIZE:
                    # 分割文件
                    chunks = file_manager.split_file(file_path, CHUNK_SIZE)
                    
                    # 发送所有分片
                    for i, chunk_file in enumerate(chunks):
                        chunk_caption = f"{title}\n\n**分片 {i+1}/{len(chunks)}**"
                        await client.send_document(
                            chat_id=message.chat.id,
                            document=chunk_file,
                            caption=chunk_caption,
                            thumb=screenshot_path if screenshot_path else None
                        )
                    
                    # 清理分片文件
                    for chunk_file in chunks:
                        if chunk_file != file_path and os.path.exists(chunk_file):
                            file_manager.safe_remove(chunk_file)
                else:
                    # 直接发送文件
                    await client.send_document(
                        chat_id=message.chat.id,
                        document=file_path,
                        caption=title,
                        thumb=screenshot_path if screenshot_path else None
                    )
                
                # 清理截图文件
                if screenshot_path and os.path.exists(screenshot_path):
                    os.remove(screenshot_path)
            
            # 更新流量统计
            await traffic_service.update_user_traffic(user_id, file_size)
            
            # 清理临时文件
            download_service.cleanup(file_path)
            
            # 删除处理中的消息
            await processing_msg.delete()
            
        except DownloadFailedException as e:
            await message.reply(f"下载失败: {e}")
        except Exception as e:
            logger.error(f"处理 Pyrogram 下载命令时出错: {e}")
            await message.reply(f"处理命令时出错: {e}")
    
    async def on_unload(self):
        """卸载插件"""
        logger.info("卸载下载命令插件")
        # Telethon 事件处理器会在客户端停止时自动清理
        # Pyrogram 事件处理器会在客户端停止时自动清理
    
    def get_help_text(self) -> str:
        """获取插件帮助文本"""
        return """下载命令：
/dl <视频链接> - 下载视频
/adl <视频链接> - 下载音频
支持 YouTube、Instagram、Facebook 等平台"""


# 创建插件实例并注册
download_commands = DownloadCommands()
_plugin_registry.register(download_commands)