"""配置验证器

提供配置验证功能，确保配置的完整性和正确性。
"""
import os
import re
import logging
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

from ..config import settings, ConfigError

logger = logging.getLogger(__name__)


class ConfigValidator:
    """配置验证器类"""
    
    def __init__(self):
        """初始化配置验证器"""
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_all(self) -> bool:
        """验证所有配置项
        
        Returns:
            True表示所有配置验证通过，False表示存在错误
        """
        self.errors.clear()
        self.warnings.clear()
        
        # 验证基本配置
        self._validate_telegram_config()
        self._validate_database_config()
        self._validate_proxy_config()
        self._validate_performance_config()
        self._validate_security_config()
        self._validate_environment_config()
        
        # 记录验证结果
        if self.errors:
            logger.error("配置验证失败，发现 %d 个错误", len(self.errors))
            for error in self.errors:
                logger.error("  • %s", error)
        
        if self.warnings:
            logger.warning("配置验证发现 %d 个警告", len(self.warnings))
            for warning in self.warnings:
                logger.warning("  • %s", warning)
        
        return len(self.errors) == 0
    
    def _validate_telegram_config(self) -> None:
        """验证Telegram相关配置"""
        # API_ID验证
        if not settings.API_ID:
            self.errors.append("API_ID 不能为空")
        elif not isinstance(settings.API_ID, int) or settings.API_ID <= 0:
            self.errors.append("API_ID 必须为正整数")
        
        # API_HASH验证
        if not settings.API_HASH:
            self.errors.append("API_HASH 不能为空")
        elif len(settings.API_HASH) != 32:
            self.errors.append("API_HASH 长度必须为32位")
        elif not settings.API_HASH.isalnum():
            self.errors.append("API_HASH 必须为字母数字组合")
        
        # BOT_TOKEN验证
        if not settings.BOT_TOKEN:
            self.errors.append("BOT_TOKEN 不能为空")
        elif not re.match(r'^\d+:\w+$', settings.BOT_TOKEN):
            self.errors.append("BOT_TOKEN 格式无效，应为 '数字:字符串' 格式")
        
        # AUTH验证
        if not settings.AUTH:
            self.errors.append("AUTH 不能为空")
        else:
            try:
                auth_users = settings.get_auth_users()
                if not auth_users:
                    self.errors.append("AUTH 必须包含有效的用户ID")
                for user_id in auth_users:
                    if not isinstance(user_id, int) or user_id <= 0:
                        self.errors.append(f"AUTH 中的用户ID {user_id} 无效")
            except (ValueError, TypeError) as e:
                self.errors.append(f"AUTH 格式无效: {e}")
    
    def _validate_database_config(self) -> None:
        """验证数据库配置"""
        if not settings.MONGO_DB:
            self.errors.append("MONGO_DB 不能为空")
            return
        
        # 验证MongoDB连接字符串格式
        if not settings.MONGO_DB.startswith(('mongodb://', 'mongodb+srv://')):
            self.errors.append("MONGO_DB 必须是有效的MongoDB连接字符串")
        
        # 尝试解析连接字符串
        try:
            parsed = urlparse(settings.MONGO_DB)
            if not parsed.netloc:
                self.errors.append("MONGO_DB 连接字符串格式错误")
        except Exception as e:
            self.errors.append(f"MONGO_DB 连接字符串解析失败: {e}")
    
    def _validate_proxy_config(self) -> None:
        """验证代理配置"""
        proxy_config = settings.get_proxy_config()
        
        if proxy_config:
            # 验证代理类型
            if proxy_config["scheme"] not in ['http', 'https', 'socks4', 'socks5']:
                self.errors.append(f"不支持的代理协议: {proxy_config['scheme']}")
            
            # 验证主机和端口
            if not proxy_config["hostname"]:
                self.errors.append("代理主机不能为空")
            
            if not (1 <= proxy_config["port"] <= 65535):
                self.errors.append(f"代理端口无效: {proxy_config['port']}")
        else:
            # 检查是否有部分代理配置
            proxy_attrs = [
                settings.TELEGRAM_PROXY_SCHEME,
                settings.TELEGRAM_PROXY_HOST,
                settings.TELEGRAM_PROXY_PORT
            ]
            
            proxy_count = sum(1 for attr in proxy_attrs if attr is not None)
            if proxy_count > 0:
                self.errors.append("代理配置不完整，必须同时设置 SCHEME、HOST 和 PORT")
    
    def _validate_performance_config(self) -> None:
        """验证性能相关配置"""
        # 并发配置验证
        if settings.MAX_WORKERS <= 0 or settings.MAX_WORKERS > 20:
            self.errors.append("MAX_WORKERS 必须在1-20之间")
        
        if settings.MIN_CONCURRENCY <= 0:
            self.errors.append("MIN_CONCURRENCY 必须大于0")
        
        if settings.MAX_CONCURRENCY < settings.MIN_CONCURRENCY:
            self.errors.append("MAX_CONCURRENCY 不能小于 MIN_CONCURRENCY")
        
        if settings.MAX_CONCURRENCY > 50:
            self.warnings.append("MAX_CONCURRENCY 过高可能导致性能问题")
        
        # 分块大小验证
        if settings.CHUNK_SIZE <= 0 or settings.CHUNK_SIZE > 50*1024*1024:
            self.errors.append("CHUNK_SIZE 必须在1字节到50MB之间")
        
        # 重试配置验证
        if settings.MAX_RETRIES <= 0 or settings.MAX_RETRIES > 10:
            self.errors.append("MAX_RETRIES 必须在1-10之间")
        
        if settings.RETRY_DELAY <= 0:
            self.errors.append("RETRY_DELAY 必须大于0")
        
        # 超时配置验证
        if settings.CONNECT_TIMEOUT <= 0:
            self.errors.append("CONNECT_TIMEOUT 必须大于0")
        
        if settings.READ_TIMEOUT <= 0:
            self.errors.append("READ_TIMEOUT 必须大于0")
    
    def _validate_security_config(self) -> None:
        """验证安全相关配置"""
        # 流量限制验证
        if settings.DEFAULT_DAILY_LIMIT < 0:
            self.errors.append("DEFAULT_DAILY_LIMIT 不能为负数")
        
        if settings.DEFAULT_MONTHLY_LIMIT < 0:
            self.errors.append("DEFAULT_MONTHLY_LIMIT 不能为负数")
        
        if settings.DEFAULT_PER_FILE_LIMIT < 0:
            self.errors.append("DEFAULT_PER_FILE_LIMIT 不能为负数")
        
        # 加密密钥验证（如果存在）
        if settings.ENCRYPTION_KEY:
            if len(settings.ENCRYPTION_KEY) < 16:
                self.warnings.append("ENCRYPTION_KEY 长度过短，建议至少16位")
    
    def _validate_environment_config(self) -> None:
        """验证环境相关配置"""
        # 环境验证
        if settings.ENVIRONMENT not in ['development', 'testing', 'production']:
            self.errors.append("ENVIRONMENT 必须是 development、testing 或 production")
        
        # 日志级别验证
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if settings.LOG_LEVEL.upper() not in valid_log_levels:
            self.errors.append(f"LOG_LEVEL 必须是 {', '.join(valid_log_levels)} 之一")
        
        # 健康检查端口验证
        if not (1024 <= settings.HEALTH_CHECK_PORT <= 65535):
            self.errors.append(f"HEALTH_CHECK_PORT 必须在1024-65535之间")
    
    def get_validation_report(self) -> Dict[str, Any]:
        """获取验证报告
        
        Returns:
            包含验证结果的字典
        """
        return {
            "valid": len(self.errors) == 0,
            "errors": self.errors.copy(),
            "warnings": self.warnings.copy(),
            "error_count": len(self.errors),
            "warning_count": len(self.warnings)
        }
    
    def generate_config_template(self) -> Dict[str, Any]:
        """生成配置模板
        
        Returns:
            配置模板字典
        """
        return {
            "API_ID": "",
            "API_HASH": "",
            "BOT_TOKEN": "",
            "AUTH": "",
            "MONGO_DB": "",
            "ENVIRONMENT": "production",
            "LOG_LEVEL": "INFO",
            "MAX_WORKERS": 3,
            "MIN_CONCURRENCY": 1,
            "MAX_CONCURRENCY": 15,
            "CHUNK_SIZE": 524288,
            "DEFAULT_DAILY_LIMIT": 1073741824,
            "DEFAULT_MONTHLY_LIMIT": 10737418240,
            "DEFAULT_PER_FILE_LIMIT": 104857600,
            "MAX_RETRIES": 3,
            "RETRY_DELAY": 1.0,
            "CONNECT_TIMEOUT": 30,
            "READ_TIMEOUT": 60,
            "HEALTH_CHECK_PORT": 8080
        }


def ensure_config_integrity() -> bool:
    """确保配置完整性
    
    Returns:
        True表示配置完整且正确，False表示存在问题
    """
    try:
        validator = ConfigValidator()
        is_valid = validator.validate_all()
        
        if not is_valid:
            report = validator.get_validation_report()
            logger.error("配置完整性检查失败，发现 %d 个错误", report["error_count"])
            
            # 如果是在开发环境，提供更详细的帮助信息
            if not settings.is_production():
                logger.info("配置模板参考:")
                template = validator.generate_config_template()
                for key, value in template.items():
                    logger.info("  %s=%s", key, value)
        
        return is_valid
        
    except Exception as e:
        logger.error("配置完整性检查时发生错误: %s", e)
        return False


def validate_specific_config(config_key: str, config_value: Any) -> bool:
    """验证特定配置项
    
    Args:
        config_key: 配置项键名
        config_value: 配置项值
        
    Returns:
        True表示配置项有效，False表示无效
    """
    validators = {
        "API_ID": lambda v: isinstance(v, int) and v > 0,
        "API_HASH": lambda v: isinstance(v, str) and len(v) == 32 and v.isalnum(),
        "BOT_TOKEN": lambda v: isinstance(v, str) and bool(re.match(r'^\d+:\w+$', v)),
        "AUTH": lambda v: bool(v) and isinstance(v, (int, str)),
        "MONGO_DB": lambda v: isinstance(v, str) and v.startswith(('mongodb://', 'mongodb+srv://')),
        "ENVIRONMENT": lambda v: v in ['development', 'testing', 'production'],
        "LOG_LEVEL": lambda v: v.upper() in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    }
    
    if config_key not in validators:
        logger.warning("未知的配置项: %s", config_key)
        return True  # 未知配置项默认认为有效
    
    try:
        return validators[config_key](config_value)
    except Exception as e:
        logger.error("验证配置项 %s 时发生错误: %s", config_key, e)
        return False


# 创建全局验证器实例
config_validator = ConfigValidator()