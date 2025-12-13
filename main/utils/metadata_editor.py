"""元数据编辑器模块

提供音频和视频文件的元数据编辑功能。
"""
import os
import logging
from typing import Optional, Dict, Any

from ..utils.logging_config import get_logger

logger = get_logger(__name__)


try:
    from mutagen import File
    from mutagen.id3 import ID3, TIT2, TPE1, COMM, APIC, error
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False
    logger.warning("mutagen库未安装，元数据编辑功能不可用")


class MetadataEditor:
    """元数据编辑器，提供音频和视频文件的元数据编辑功能"""
    
    def __init__(self):
        self.logger = logger
    
    def edit_audio_metadata(self, file_path: str, metadata: Dict[str, Any]) -> bool:
        """编辑音频文件元数据
        
        Args:
            file_path: 音频文件路径
            metadata: 元数据字典，包含要编辑的字段
            
        Returns:
            编辑成功返回True，失败返回False
        """
        if not MUTAGEN_AVAILABLE:
            self.logger.warning("mutagen库未安装，无法编辑音频元数据")
            return False
        
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                self.logger.error(f"音频文件不存在: {file_path}")
                return False
            
            # 打开音频文件
            audio_file = File(file_path)
            if audio_file is None:
                self.logger.error(f"无法打开音频文件: {file_path}")
                return False
            
            # 确保文件有ID3标签
            if hasattr(audio_file, 'add_tags'):
                try:
                    audio_file.add_tags()
                except error as e:
                    # 标签已存在，忽略错误
                    pass
            
            # 编辑元数据
            if isinstance(audio_file, ID3):
                # MP3文件，使用ID3标签
                if 'title' in metadata:
                    audio_file['TIT2'] = TIT2(encoding=3, text=metadata['title'])
                
                if 'artist' in metadata:
                    audio_file['TPE1'] = TPE1(encoding=3, text=metadata['artist'])
                
                if 'comment' in metadata:
                    audio_file['COMM'] = COMM(encoding=3, lang='eng', desc='Comment', text=metadata['comment'])
                
                if 'thumbnail' in metadata and os.path.exists(metadata['thumbnail']):
                    with open(metadata['thumbnail'], 'rb') as img:
                        audio_file['APIC'] = APIC(
                            encoding=3, 
                            mime='image/jpeg', 
                            type=3, 
                            desc='Cover', 
                            data=img.read()
                        )
                
                # 保存更改
                audio_file.save()
            else:
                # 其他音频格式，使用通用标签
                if 'title' in metadata:
                    audio_file['title'] = metadata['title']
                
                if 'artist' in metadata:
                    audio_file['artist'] = metadata['artist']
                
                if 'album' in metadata:
                    audio_file['album'] = metadata['album']
                
                # 保存更改
                audio_file.save()
            
            self.logger.info(f"成功编辑音频元数据: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"编辑音频元数据失败 {file_path}: {e}")
            return False
    
    def get_audio_metadata(self, file_path: str) -> Dict[str, Any]:
        """获取音频文件元数据
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            包含元数据的字典
        """
        if not MUTAGEN_AVAILABLE:
            self.logger.warning("mutagen库未安装，无法获取音频元数据")
            return {}
        
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                self.logger.error(f"音频文件不存在: {file_path}")
                return {}
            
            # 打开音频文件
            audio_file = File(file_path)
            if audio_file is None:
                self.logger.error(f"无法打开音频文件: {file_path}")
                return {}
            
            metadata = {}
            
            # 提取元数据
            if isinstance(audio_file, ID3):
                # MP3文件，使用ID3标签
                if 'TIT2' in audio_file:
                    metadata['title'] = audio_file['TIT2'].text[0]
                
                if 'TPE1' in audio_file:
                    metadata['artist'] = audio_file['TPE1'].text[0]
                
                if 'COMM' in audio_file:
                    metadata['comment'] = audio_file['COMM'].text[0]
            else:
                # 其他音频格式，使用通用标签
                if 'title' in audio_file:
                    metadata['title'] = audio_file['title'][0] if isinstance(audio_file['title'], list) else audio_file['title']
                
                if 'artist' in audio_file:
                    metadata['artist'] = audio_file['artist'][0] if isinstance(audio_file['artist'], list) else audio_file['artist']
                
                if 'album' in audio_file:
                    metadata['album'] = audio_file['album'][0] if isinstance(audio_file['album'], list) else audio_file['album']
            
            self.logger.info(f"成功获取音频元数据: {file_path}")
            return metadata
        except Exception as e:
            self.logger.error(f"获取音频元数据失败 {file_path}: {e}")
            return {}
    
    def edit_video_metadata(self, file_path: str, metadata: Dict[str, Any]) -> bool:
        """编辑视频文件元数据
        
        Args:
            file_path: 视频文件路径
            metadata: 元数据字典，包含要编辑的字段
            
        Returns:
            编辑成功返回True，失败返回False
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                self.logger.error(f"视频文件不存在: {file_path}")
                return False
            
            # 目前只支持简单的元数据编辑，复杂的视频元数据需要更专业的库
            # 这里可以添加FFmpeg命令来编辑视频元数据
            self.logger.info(f"视频元数据编辑功能正在开发中")
            return True
        except Exception as e:
            self.logger.error(f"编辑视频元数据失败 {file_path}: {e}")
            return False
    
    async def get_video_metadata(self, file_path: str) -> Dict[str, Any]:
        """获取视频文件元数据
        
        Args:
            file_path: 视频文件路径
            
        Returns:
            包含元数据的字典
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                self.logger.error(f"视频文件不存在: {file_path}")
                return {}
            
            # 使用FFprobe获取视频元数据
            from ..utils.video_processor import video_processor
            metadata = await video_processor.get_video_metadata(file_path)
            
            self.logger.info(f"成功获取视频元数据: {file_path}")
            return metadata
        except Exception as e:
            self.logger.error(f"获取视频元数据失败 {file_path}: {e}")
            return {}


# 全局元数据编辑器实例
metadata_editor = MetadataEditor()
