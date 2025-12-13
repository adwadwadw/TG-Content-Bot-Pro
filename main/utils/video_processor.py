"""视频处理工具模块

提供视频截图生成、视频元数据提取等功能。
"""
import os
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class VideoProcessor:
    """视频处理器，提供视频截图生成和元数据提取功能"""
    
    def __init__(self):
        self.logger = logger
    
    async def screenshot(self, video_path: str, duration: int, sender_id: str) -> Optional[str]:
        """生成视频截图
        
        Args:
            video_path: 视频文件路径
            duration: 视频时长（秒）
            sender_id: 发送者ID，用于生成临时文件名
            
        Returns:
            截图文件路径，生成失败返回None
        """
        try:
            # 检查视频文件是否存在
            if not os.path.exists(video_path):
                self.logger.error(f"视频文件不存在: {video_path}")
                return None
            
            # 计算截图时间点（视频中间位置）
            timestamp = self._format_timestamp(duration // 2)
            
            # 生成输出文件名
            output_file = f"screenshot_{sender_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            
            # 构建FFmpeg命令
            cmd = [
                "ffmpeg",
                "-ss", timestamp,
                "-i", video_path,
                "-frames:v", "1",
                output_file,
                "-y",  # 覆盖现有文件
                "-hide_banner",
                "-loglevel", "error"
            ]
            
            # 执行FFmpeg命令
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # 检查命令执行结果
            if process.returncode != 0:
                self.logger.error(f"FFmpeg执行失败: {stderr.decode().strip()}")
                return None
            
            # 检查截图文件是否生成
            if os.path.exists(output_file):
                self.logger.info(f"视频截图生成成功: {output_file}")
                return output_file
            else:
                self.logger.error(f"截图文件未生成: {output_file}")
                return None
            
        except Exception as e:
            self.logger.error(f"生成视频截图时出错: {e}")
            return None
    
    def _format_timestamp(self, seconds: int) -> str:
        """将秒数格式化为FFmpeg可用的时间戳（HH:MM:SS）
        
        Args:
            seconds: 秒数
            
        Returns:
            格式化的时间戳字符串
        """
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        remaining_seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{remaining_seconds:02d}"
    
    async def get_video_metadata(self, video_path: str) -> Dict[str, Any]:
        """提取视频元数据
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            包含视频宽度、高度、时长等信息的字典
        """
        try:
            # 构建FFprobe命令
            cmd = [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height,duration",
                "-of", "json",
                video_path
            ]
            
            # 执行FFprobe命令
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # 检查命令执行结果
            if process.returncode != 0:
                self.logger.error(f"FFprobe执行失败: {stderr.decode().strip()}")
                return {"width": 0, "height": 0, "duration": 0}
            
            # 解析JSON输出
            import json
            metadata = json.loads(stdout.decode())
            
            if "streams" in metadata and metadata["streams"]:
                stream = metadata["streams"][0]
                return {
                    "width": int(stream.get("width", 0)),
                    "height": int(stream.get("height", 0)),
                    "duration": float(stream.get("duration", 0))
                }
            else:
                self.logger.error(f"无法提取视频元数据: {video_path}")
                return {"width": 0, "height": 0, "duration": 0}
            
        except Exception as e:
            self.logger.error(f"提取视频元数据时出错: {e}")
            return {"width": 0, "height": 0, "duration": 0}


# 创建全局视频处理器实例
video_processor = VideoProcessor()
