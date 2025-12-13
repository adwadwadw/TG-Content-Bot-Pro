"""视频下载服务模块

提供多平台视频下载功能，基于 yt-dlp 实现。
"""
import os
import asyncio
import logging
import tempfile
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
from urllib.parse import urlparse

import yt_dlp

from ..config import settings
from ..utils.logging_config import get_logger
from ..utils.file_manager import FileManager
from ..utils.video_processor import video_processor
from ..exceptions.telegram import DownloadFailedException

logger = get_logger(__name__)


class VideoDownloader:
    """视频下载器"""
    
    def __init__(self):
        self.file_manager = FileManager()
        self.temp_dir = tempfile.mkdtemp()
        self.progress_callbacks = {}
        self.logger = logging.getLogger(__name__)
        
    def _download_progress_hook(self, d: Dict[str, Any]) -> None:
        """下载进度钩子"""
        if d['status'] == 'downloading':
            # 记录下载进度
            percent = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            filename = d.get('filename', '未知文件')
            logger.debug(f"下载进度: {percent} | 速度: {speed} | 剩余时间: {eta}")
            
            # 调用进度回调
            callback = self.progress_callbacks.get(filename)
            if callback:
                callback({
                    'status': 'downloading',
                    'percent': percent,
                    'speed': speed,
                    'eta': eta,
                    'filename': filename
                })
        elif d['status'] == 'error':
            error_msg = d.get('error', '未知错误')
            logger.error(f"下载错误: {error_msg}")
            
            # 调用进度回调
            filename = d.get('filename', '未知文件')
            callback = self.progress_callbacks.get(filename)
            if callback:
                callback({
                    'status': 'error',
                    'error': error_msg,
                    'filename': filename
                })
        elif d['status'] == 'finished':
            filename = d.get('filename', '未知文件')
            logger.info(f"下载完成: {filename}")
            
            # 调用进度回调
            callback = self.progress_callbacks.get(filename)
            if callback:
                callback({
                    'status': 'finished',
                    'filename': filename
                })
    
    async def download_video(self, url: str, quality: str = 'best', progress_callback: Optional[callable] = None) -> Tuple[str, str, int, float]:
        """下载视频
        
        Args:
            url: 视频链接
            quality: 视频质量，可选值：best, worst, bestvideo, bestaudio
            progress_callback: 进度回调函数，接收下载进度信息
            
        Returns:
            视频文件路径, 视频标题, 文件大小, 视频时长
            
        Raises:
            DownloadFailedException: 下载失败时抛出
        """
        try:
            logger.info(f"开始下载视频: {url}")
            
            # 验证 URL 格式
            if not self._is_valid_url(url):
                raise DownloadFailedException(f"无效的URL格式: {url}")
            
            # yt-dlp 配置
            ytdl_opts = {
                'outtmpl': os.path.join(self.temp_dir, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'merge_output_format': 'mp4',
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'progress_hooks': [self._download_progress_hook],
            }
            
            # 添加Cookie支持
            from ..config import settings
            url_domain = urlparse(url).netloc
            if 'youtube.com' in url_domain or 'youtu.be' in url_domain and settings.YT_COOKIES:
                # 创建临时Cookie文件
                temp_cookie_path = os.path.join(self.temp_dir, 'youtube_cookies.txt')
                with open(temp_cookie_path, 'w') as f:
                    f.write(settings.YT_COOKIES)
                ytdl_opts['cookiefile'] = temp_cookie_path
                logger.info("已添加YouTube Cookie支持")
            elif 'instagram.com' in url_domain and settings.INSTA_COOKIES:
                # 创建临时Cookie文件
                temp_cookie_path = os.path.join(self.temp_dir, 'instagram_cookies.txt')
                with open(temp_cookie_path, 'w') as f:
                    f.write(settings.INSTA_COOKIES)
                ytdl_opts['cookiefile'] = temp_cookie_path
                logger.info("已添加Instagram Cookie支持")
            
            # 根据质量调整 yt-dlp 配置
            opts = ytdl_opts.copy()
            if quality == 'worst':
                opts['format'] = 'worstvideo[ext=mp4]+worstaudio[ext=m4a]/worst[ext=mp4]/worst'
            elif quality == 'bestaudio':
                opts['format'] = 'bestaudio[ext=m4a]/bestaudio'
                opts['postprocessors'] = [{    # 只提取音频
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            
            # 使用 yt-dlp 下载视频
            loop = asyncio.get_event_loop()
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = await loop.run_in_executor(None, ydl.extract_info, url, False)
                filename = await loop.run_in_executor(None, ydl.prepare_filename, info)
                
                # 注册进度回调
                if progress_callback:
                    self.progress_callbacks[filename] = progress_callback
                
                await loop.run_in_executor(None, ydl.download, [url])
            
            # 检查文件是否存在
            if not os.path.exists(filename):
                # 尝试查找实际文件名（因为 yt-dlp 可能会更改文件名）
                temp_files = list(Path(self.temp_dir).glob('*'))
                if not temp_files:
                    raise DownloadFailedException("下载的文件不存在")
                filename = str(temp_files[0])
            
            # 获取文件大小
            file_size = os.path.getsize(filename)
            
            # 获取视频标题
            title = info.get('title', '未命名视频')
            
            # 获取视频时长
            duration = float(info.get('duration', 0))
            
            # 清理进度回调
            if filename in self.progress_callbacks:
                del self.progress_callbacks[filename]
            
            # 编辑音频元数据（如果是音频文件）
            if quality == 'bestaudio':
                from ..utils.metadata_editor import metadata_editor
                # 提取文件扩展名
                ext = os.path.splitext(filename)[1].lower()
                if ext in ['.mp3', '.m4a', '.wav', '.flac', '.ogg']:
                    # 编辑音频元数据
                    metadata = {
                        'title': title,
                        'artist': 'TG-Content-Bot-Pro',
                        'comment': 'Downloaded with TG-Content-Bot-Pro'
                    }
                    metadata_editor.edit_audio_metadata(filename, metadata)
                    logger.info(f"已更新音频元数据: {title}")
            
            logger.info(f"视频下载成功: {title}, 文件大小: {file_size} 字节, 时长: {duration} 秒")
            return filename, title, file_size, duration
        except yt_dlp.DownloadError as e:
            logger.error(f"yt-dlp 下载错误: {e}")
            raise DownloadFailedException(f"视频下载失败: {str(e)}")
        except Exception as e:
            logger.error(f"下载视频时发生未知错误: {e}")
            raise DownloadFailedException(f"视频下载失败: {str(e)}")
    
    async def download_audio(self, url: str, quality: str = 'best', progress_callback: Optional[callable] = None) -> Tuple[str, str, int]:
        """下载音频
        
        Args:
            url: 视频链接
            quality: 音频质量，可选值：best, worst
            progress_callback: 进度回调函数，接收下载进度信息
            
        Returns:
            音频文件路径, 音频标题, 文件大小
            
        Raises:
            DownloadFailedException: 下载失败时抛出
        """
        # 调用download_video方法获取音频，忽略返回的时长
        file_path, title, file_size, _ = await self.download_video(url, quality='bestaudio', progress_callback=progress_callback)
        return file_path, title, file_size
    
    def _is_valid_url(self, url: str) -> bool:
        """验证 URL 格式
        
        Args:
            url: 要验证的 URL
            
        Returns:
            True 表示 URL 格式有效，False 表示无效
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def cleanup(self, file_path: str) -> None:
        """清理临时文件
        
        Args:
            file_path: 要清理的文件路径
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"已清理临时文件: {file_path}")
        except Exception as e:
            logger.error(f"清理临时文件时出错: {e}")
    
    def cleanup_all(self) -> None:
        """清理所有临时文件"""
        try:
            if os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir)
                logger.debug(f"已清理所有临时文件: {self.temp_dir}")
        except Exception as e:
            logger.error(f"清理所有临时文件时出错: {e}")

    async def download_message(self, userbot, client, telethon_bot, sender, edit_id, msg_link, offset):
        """处理Telegram消息链接下载
        
        Args:
            userbot: Userbot客户端
            client: Pyrogram客户端
            telethon_bot: Telethon客户端
            sender: 发送者ID
            edit_id: 要编辑的消息ID
            msg_link: 消息链接
            offset: 偏移量
        
        Returns:
            bool: 下载是否成功
        """
        try:
            self.logger.info(f"开始处理消息链接: {msg_link}")
            
            # 解析消息链接
            import re
            link_pattern = r'(?:https?://)?(?:t\.me|telegram\.me)/(\w+)/(\d+)'  # 匹配格式: t.me/channel_name/123
            match = re.match(link_pattern, msg_link)
            
            if not match:
                self.logger.error(f"无效的消息链接格式: {msg_link}")
                # 直接发送新消息，不尝试编辑
                await telethon_bot.send_message(sender, "❌ 无效的消息链接格式")
                return False
            
            chat_id = match.group(1)
            message_id = int(match.group(2)) + offset
            
            self.logger.info(f"解析链接结果: chat_id={chat_id}, message_id={message_id}")
            
            # 发送处理状态
            await telethon_bot.send_message(sender, "✅ 正在下载媒体...")
            
            # 下载媒体
            if userbot:
                # 使用Userbot下载
                try:
                    self.logger.info("使用Userbot下载媒体")
                    # 这里应该实现Userbot下载逻辑
                    # 例如: message = await userbot.get_messages(chat_id, message_id)
                    # 然后下载媒体并发送给用户
                    await telethon_bot.send_message(sender, "✅ Userbot下载功能开发中")
                    return True
                except Exception as e:
                    self.logger.error(f"Userbot下载失败: {e}")
                    await telethon_bot.send_message(sender, f"❌ Userbot下载失败: {str(e)}")
                    return False
            else:
                # 使用Telethon Bot下载
                try:
                    self.logger.info("使用Telethon Bot下载媒体")
                    # 这里应该实现Telethon Bot下载逻辑
                    # 例如: message = await telethon_bot.get_messages(chat_id, message_id)
                    # 然后下载媒体并发送给用户
                    await telethon_bot.send_message(sender, "✅ 正在获取消息...")
                    # 尝试获取消息
                    try:
                        # 获取聊天实体
                        chat_entity = await telethon_bot.get_entity(chat_id)
                        await telethon_bot.send_message(sender, f"✅ 已找到聊天实体: {chat_entity.title if hasattr(chat_entity, 'title') else chat_id}")
                        
                        # 尝试获取消息
                        message = await telethon_bot.get_messages(chat_entity, ids=message_id)
                        await telethon_bot.send_message(sender, f"✅ 已获取消息: {message.id}")
                        
                        # 检查消息是否包含媒体
                        if message.media:
                            await telethon_bot.send_message(sender, "✅ 消息包含媒体，开始下载...")
                            # 这里应该实现媒体下载逻辑
                            await telethon_bot.send_message(sender, "✅ 媒体下载功能开发中")
                            return True
                        else:
                            await telethon_bot.send_message(sender, "❌ 消息不包含媒体")
                            return False
                    except Exception as e:
                        self.logger.error(f"获取消息失败: {e}")
                        await telethon_bot.send_message(sender, f"❌ 获取消息失败: {str(e)}")
                        return False
                except Exception as e:
                    self.logger.error(f"Telethon Bot下载失败: {e}")
                    await telethon_bot.send_message(sender, f"❌ 下载失败: {str(e)}")
                    return False
        except Exception as e:
            self.logger.error(f"处理消息链接时出错: {e}", exc_info=True)
            await telethon_bot.send_message(sender, f"❌ 处理失败: {str(e)}")
            return False


# 创建全局下载器实例
download_service = VideoDownloader()