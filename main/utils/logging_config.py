"""日志配置模块

提供高级日志配置功能，包括日志轮转、结构化日志和性能优化。
"""
import logging
import os
import glob
import sys
import json
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Dict, Any, Optional

from ..config import settings


class StructuredFormatter(logging.Formatter):
    """结构化日志格式化器"""
    
    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None):
        super().__init__(fmt, datefmt)
        self.enable_json = settings.ENVIRONMENT == "production"
    
    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录
        
        Args:
            record: 日志记录
            
        Returns:
            格式化后的日志字符串
        """
        if self.enable_json:
            # 生产环境使用JSON格式
            log_data = {
                "timestamp": self.formatTime(record, self.datefmt),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno
            }
            
            # 添加额外字段
            if hasattr(record, 'user_id') and record.user_id:
                log_data["user_id"] = record.user_id
            
            if hasattr(record, 'chat_id') and record.chat_id:
                log_data["chat_id"] = record.chat_id
            
            if hasattr(record, 'message_id') and record.message_id:
                log_data["message_id"] = record.message_id
            
            if record.exc_info:
                log_data["exception"] = self.formatException(record.exc_info)
            
            return json.dumps(log_data, ensure_ascii=False)
        else:
            # 开发环境使用易读格式
            return super().format(record)


def setup_logging():
    """设置日志配置 - 支持日志轮转和结构化日志"""
    # 创建日志目录
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 配置日志级别
    log_level_name = settings.LOG_LEVEL.upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    
    # 清除现有的处理器
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建格式化器
    if settings.ENVIRONMENT == "production":
        # 生产环境：JSON格式
        formatter = StructuredFormatter()
    else:
        # 开发环境：详细的可读格式
        log_format = '[%(levelname)8s/%(asctime)s] %(name)25s:%(lineno)4d [%(funcName)15s]: %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        formatter = StructuredFormatter(log_format, date_format)
    
    # 控制台处理器（开发环境）
    if settings.ENVIRONMENT != "production":
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # 文件处理器 - 按时间轮转
    if settings.ENVIRONMENT == "production":
        # 生产环境：按天轮转，保留30天
        log_file = os.path.join(log_dir, "bot.log")
        file_handler = TimedRotatingFileHandler(
            log_file,
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
    else:
        # 开发环境：按大小轮转，最大10MB，保留5个备份
        log_file = os.path.join(log_dir, "bot_debug.log")
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
    
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # 错误日志单独处理
    error_log_file = os.path.join(log_dir, "error.log")
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=10,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)
    
    # 设置根日志级别
    root_logger.setLevel(log_level)
    
    # 优化第三方库日志级别
    self._optimize_third_party_logging()
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 70)
    logger.info("🎯 高级日志系统初始化完成")
    logger.info("📁 日志文件: %s", log_file)
    logger.info("🔧 日志级别: %s", log_level_name)
    logger.info("🌍 环境: %s", settings.ENVIRONMENT)
    logger.info("📊 格式: %s", "JSON" if settings.ENVIRONMENT == "production" else "文本")
    logger.info("=" * 70)
    
    return logger


def _optimize_third_party_logging():
    """优化第三方库的日志级别"""
    # 减少第三方库的日志噪音
    noisy_modules = [
        ("pyrogram", logging.WARNING),
        ("telethon", logging.WARNING),
        ("pymongo", logging.WARNING),
        ("urllib3", logging.WARNING),
        ("httpx", logging.WARNING),
        ("asyncio", logging.WARNING),
        ("aiohttp", logging.WARNING)
    ]
    
    for module_name, level in noisy_modules:
        logging.getLogger(module_name).setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """获取命名日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        日志记录器实例
    """
    logger = logging.getLogger(name)
    
    # 为特定模块设置优化级别
    if name.startswith("main.services"):
        logger.setLevel(logging.INFO)
    elif name.startswith("main.core"):
        logger.setLevel(logging.INFO)
    
    return logger


def log_with_context(logger: logging.Logger, level: int, message: str, 
                    user_id: Optional[int] = None,
                    chat_id: Optional[int] = None,
                    message_id: Optional[int] = None,
                    **kwargs) -> None:
    """带上下文的日志记录
    
    Args:
        logger: 日志记录器
        level: 日志级别
        message: 日志消息
        user_id: 用户ID
        chat_id: 聊天ID
        message_id: 消息ID
        **kwargs: 额外上下文
    """
    # 创建日志记录
    if logger.isEnabledFor(level):
        record = logger.makeRecord(
            logger.name, level, "", 0, message, (), None,
            func=kwargs.get('func'), extra=kwargs
        )
        
        # 添加上下文信息
        if user_id:
            record.user_id = user_id
        if chat_id:
            record.chat_id = chat_id
        if message_id:
            record.message_id = message_id
        
        logger.handle(record)


class PerformanceLogger:
    """性能日志记录器"""
    
    def __init__(self, logger: logging.Logger):
        """初始化性能日志记录器
        
        Args:
            logger: 基础日志记录器
        """
        self.logger = logger
        self.performance_threshold_ms = 1000  # 性能阈值（毫秒）
    
    def log_performance(self, operation: str, duration_ms: float, 
                       success: bool = True, 
                       user_id: Optional[int] = None,
                       details: Optional[Dict[str, Any]] = None) -> None:
        """记录性能日志
        
        Args:
            operation: 操作名称
            duration_ms: 耗时（毫秒）
            success: 是否成功
            user_id: 用户ID
            details: 详细信息
        """
        level = logging.INFO if success else logging.ERROR
        
        # 构建性能消息
        status = "✅" if success else "❌"
        message = f"{status} {operation} - 耗时: {duration_ms:.2f}ms"
        
        if details:
            message += f" | 详情: {json.dumps(details, ensure_ascii=False)}"
        
        # 记录日志
        log_with_context(self.logger, level, message, user_id=user_id)
        
        # 记录慢操作警告
        if duration_ms > self.performance_threshold_ms:
            self.logger.warning("🐌 慢操作检测: %s 耗时 %.2fms", operation, duration_ms)
    
    def set_threshold(self, threshold_ms: float) -> None:
        """设置性能阈值
        
        Args:
            threshold_ms: 阈值（毫秒）
        """
        self.performance_threshold_ms = threshold_ms


# 创建全局性能日志记录器
performance_logger = PerformanceLogger(get_logger(__name__))


def get_logger(name: str) -> logging.Logger:
    """获取命名日志记录器"""
    return logging.getLogger(name)