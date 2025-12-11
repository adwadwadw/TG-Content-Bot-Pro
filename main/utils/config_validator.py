"""
配置验证工具
提供环境变量配置的完整性检查和验证功能
"""
import os
import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class ConfigValidator:
    """配置验证器"""
    
    def __init__(self, settings):
        self.settings = settings
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """验证所有配置"""
        self.errors.clear()
        self.warnings.clear()
        
        # 验证必需配置
        self._validate_required()
        
        # 验证格式和类型
        self._validate_formats()
        
        # 验证逻辑一致性
        self._validate_logic()
        
        # 验证可选配置
        self._validate_optional()
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _validate_required(self):
        """验证必需配置"""
        required_configs = [
            ('API_ID', 'Telegram API ID'),
            ('API_HASH', 'Telegram API Hash'),
            ('BOT_TOKEN', 'Bot Token'),
            ('AUTH', 'Owner User ID')
        ]
        
        for config_name, description in required_configs:
            value = getattr(self.settings, config_name, None)
            if not value:
                self.errors.append(f"必需配置缺失: {description} ({config_name})")
            elif config_name == 'API_ID' and not str(value).isdigit():
                self.errors.append(f"API_ID 必须是数字: {value}")
            elif config_name == 'AUTH' and not str(value).isdigit():
                self.errors.append(f"AUTH 必须是数字: {value}")
    
    def _validate_formats(self):
        """验证配置格式"""
        # 验证 API_HASH 格式
        api_hash = getattr(self.settings, 'API_HASH', '')
        if api_hash and not re.match(r'^[a-f0-9]{32}$', api_hash, re.IGNORECASE):
            self.errors.append(f"API_HASH 格式无效: {api_hash}")
        
        # 验证 BOT_TOKEN 格式
        bot_token = getattr(self.settings, 'BOT_TOKEN', '')
        if bot_token and not re.match(r'^[0-9]+:[A-Za-z0-9_-]{35}$', bot_token):
            self.errors.append(f"Bot Token 格式无效")
        
        # 验证 MONGO_DB 格式
        mongo_db = getattr(self.settings, 'MONGO_DB', '')
        if mongo_db:
            if not mongo_db.startswith(('mongodb://', 'mongodb+srv://')):
                self.errors.append("MongoDB 连接字符串格式无效，必须以 mongodb:// 或 mongodb+srv:// 开头")
            else:
                # 验证连接字符串的基本结构
                try:
                    parsed = urlparse(mongo_db)
                    if not parsed.netloc:
                        self.errors.append("MongoDB 连接字符串格式错误")
                except Exception:
                    self.errors.append("MongoDB 连接字符串格式错误")
        
        # 验证 ENCRYPTION_KEY 格式
        encryption_key = getattr(self.settings, 'ENCRYPTION_KEY', '')
        if encryption_key and len(encryption_key) < 32:
            self.warnings.append("加密密钥长度建议至少32位")
    
    def _validate_logic(self):
        """验证逻辑一致性"""
        # 检查 SESSION 和 MongoDB 的关联
        session = getattr(self.settings, 'SESSION', '')
        mongo_db = getattr(self.settings, 'MONGO_DB', '')
        
        if session and not mongo_db:
            self.warnings.append("配置了 SESSION 但未配置 MongoDB，SESSION 管理功能可能受限")
        
        # 检查代理配置的完整性
        proxy_configs = [
            'TELEGRAM_PROXY_SCHEME',
            'TELEGRAM_PROXY_HOST', 
            'TELEGRAM_PROXY_PORT'
        ]
        
        proxy_values = [getattr(self.settings, config, '') for config in proxy_configs]
        proxy_set_count = sum(1 for value in proxy_values if value)
        
        if proxy_set_count > 0 and proxy_set_count < len(proxy_configs):
            self.warnings.append("代理配置不完整，部分代理参数缺失")
        
        # 验证代理端口
        proxy_port = getattr(self.settings, 'TELEGRAM_PROXY_PORT', '')
        if proxy_port and not str(proxy_port).isdigit():
            self.errors.append("代理端口必须是数字")
        elif proxy_port and not (1 <= int(proxy_port) <= 65535):
            self.errors.append(f"代理端口范围无效: {proxy_port}")
    
    def _validate_optional(self):
        """验证可选配置"""
        # 验证 FORCESUB 频道格式
        forcesub = getattr(self.settings, 'FORCESUB', '')
        if forcesub and forcesub.startswith('@'):
            self.warnings.append("FORCESUB 不应包含 @ 符号，只包含用户名")
        
        # 验证日志级别
        log_level = getattr(self.settings, 'LOG_LEVEL', 'INFO')
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if log_level and log_level.upper() not in valid_levels:
            self.warnings.append(f"日志级别无效: {log_level}，使用默认值 INFO")
    
    def get_health_report(self) -> Dict[str, Any]:
        """获取配置健康报告"""
        is_valid, errors, warnings = self.validate_all()
        
        return {
            'is_valid': is_valid,
            'errors': errors,
            'warnings': warnings,
            'error_count': len(errors),
            'warning_count': len(warnings),
            'required_configs_present': self._get_required_configs_status()
        }
    
    def _get_required_configs_status(self) -> Dict[str, bool]:
        """获取必需配置的状态"""
        required_configs = ['API_ID', 'API_HASH', 'BOT_TOKEN', 'AUTH']
        status = {}
        
        for config in required_configs:
            value = getattr(self.settings, config, None)
            status[config] = bool(value)
        
        return status


def validate_environment() -> Tuple[bool, List[str], List[str]]:
    """验证环境变量配置"""
    from ..config import settings
    
    validator = ConfigValidator(settings)
    return validator.validate_all()


def check_config_health() -> Dict[str, Any]:
    """检查配置健康状态"""
    from ..config import settings
    
    validator = ConfigValidator(settings)
    return validator.get_health_report()


def ensure_config_integrity() -> bool:
    """确保配置完整性，如果配置无效则退出"""
    from ..config import settings
    
    validator = ConfigValidator(settings)
    is_valid, errors, warnings = validator.validate_all()
    
    if not is_valid:
        logger.error("配置验证失败，请检查以下错误:")
        for error in errors:
            logger.error(f"  ❌ {error}")
        
        for warning in warnings:
            logger.warning(f"  ⚠️  {warning}")
        
        return False
    
    if warnings:
        logger.warning("配置验证完成，有以下警告:")
        for warning in warnings:
            logger.warning(f"  ⚠️  {warning}")
    else:
        logger.info("✅ 所有配置验证通过")
    
    return True


def validate_specific_config(config_name: str, value: Any) -> Tuple[bool, str]:
    """验证特定配置项"""
    validators = {
        'API_ID': lambda v: v.isdigit() if isinstance(v, str) else isinstance(v, int),
        'API_HASH': lambda v: bool(re.match(r'^[a-f0-9]{32}$', str(v), re.IGNORECASE)),
        'BOT_TOKEN': lambda v: bool(re.match(r'^[0-9]+:[A-Za-z0-9_-]{35}$', str(v))),
        'AUTH': lambda v: str(v).isdigit(),
        'TELEGRAM_PROXY_PORT': lambda v: str(v).isdigit() and 1 <= int(v) <= 65535,
        'LOG_LEVEL': lambda v: str(v).upper() in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    }
    
    if config_name not in validators:
        return True, "配置项无特定验证规则"
    
    try:
        is_valid = validators[config_name](value)
        if is_valid:
            return True, "配置项验证通过"
        else:
            return False, f"配置项 {config_name} 格式无效"
    except Exception as e:
        return False, f"配置项验证出错: {str(e)}"


class ConfigHealthMonitor:
    """配置健康监控器"""
    
    def __init__(self, settings):
        self.settings = settings
        self.validator = ConfigValidator(settings)
        self.last_check = None
        self.health_history = []
    
    def check_health(self) -> Dict[str, Any]:
        """检查配置健康状态"""
        health_report = self.validator.get_health_report()
        self.health_history.append({
            'timestamp': self.last_check,
            'report': health_report
        })
        
        # 保留最近10次检查记录
        if len(self.health_history) > 10:
            self.health_history.pop(0)
        
        self.last_check = health_report
        return health_report
    
    def get_trend(self) -> Dict[str, Any]:
        """获取健康趋势"""
        if len(self.health_history) < 2:
            return {'has_trend': False, 'message': '数据不足无法分析趋势'}
        
        recent_reports = self.health_history[-5:]  # 最近5次检查
        error_trend = []
        warning_trend = []
        
        for report in recent_reports:
            error_trend.append(report['error_count'])
            warning_trend.append(report['warning_count'])
        
        return {
            'has_trend': True,
            'error_trend': error_trend,
            'warning_trend': warning_trend,
            'error_increasing': error_trend[-1] > error_trend[0],
            'warning_increasing': warning_trend[-1] > warning_trend[0]
        }