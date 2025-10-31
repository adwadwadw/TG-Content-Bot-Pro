"""日志配置模块"""
import logging
import os
import glob
from datetime import datetime
from ..config import settings


def setup_logging():
    """设置日志配置 - 每日日志文件，重启时添加序号"""
    # 创建日志目录
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 生成带日期和重启序号的日志文件名
    today = datetime.now().strftime("%Y%m%d")
    base_log_file = f"bot_{today}"
    
    # 查找今天的日志文件，确定重启序号
    existing_logs = glob.glob(os.path.join(log_dir, f"{base_log_file}_*.log"))
    if existing_logs:
        # 提取序号并找到最大值
        max_index = 0
        for log_file in existing_logs:
            try:
                filename = os.path.basename(log_file)
                index_str = filename.split('_')[-1].replace('.log', '')
                index = int(index_str)
                if index > max_index:
                    max_index = index
            except:
                pass
        restart_index = max_index + 1
    else:
        restart_index = 1
    
    # 日志文件路径 - 使用三位数序号格式
    log_file = os.path.join(log_dir, f"{base_log_file}_{restart_index:03d}.log")
    
    # 配置根日志记录器
    log_level_name = settings.LOG_LEVEL.upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    
    # 清除现有的处理器
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 日志格式 - 增加更多详细信息
    log_format = '[%(levelname)s/%(asctime)s] %(name)s:%(lineno)d [%(funcName)s]: %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(log_format, datefmt=date_format)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # 文件处理器（使用新的日志文件名）
    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # 添加处理器到根日志记录器
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # 为不同模块设置合理的日志级别 - 优化日志量
    logging.getLogger("pyrogram").setLevel(logging.WARNING)  # 减少Pyrogram日志级别
    logging.getLogger("telethon").setLevel(logging.WARNING)  # 减少Telethon日志级别
    logging.getLogger("pymongo").setLevel(logging.WARNING)   # 减少MongoDB日志级别
    
    # 设置合理的日志级别
    logging.getLogger("main").setLevel(log_level)
    
    # 为特定模块设置合理的日志级别
    logging.getLogger("main.services.download_service").setLevel(log_level)
    logging.getLogger("main.core.clients").setLevel(log_level)
    logging.getLogger("main.services.session_service").setLevel(log_level)
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("日志系统初始化完成")
    logger.info(f"日志文件: {log_file}")
    logger.info(f"日志级别: {log_level_name}")
    logger.info(f"环境: {settings.ENVIRONMENT}")
    logger.info("=" * 60)


def get_logger(name: str) -> logging.Logger:
    """获取命名日志记录器"""
    return logging.getLogger(name)