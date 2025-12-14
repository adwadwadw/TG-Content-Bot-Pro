#!/usr/bin/env python3
"""
插件系统测试脚本
"""
import sys
import os
import logging
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_plugin_imports():
    """测试插件导入是否成功"""
    logger.info("\n=== 测试插件导入 ===")
    
    plugins_to_test = [
        "auth_commands",

        "session_commands",
        "traffic_commands",
        "message_handler",
        "queue_commands",
        "batch",
        "start",
        "help",
        "pyroplug"
    ]
    
    success_count = 0
    for plugin_name in plugins_to_test:
        try:
            module = __import__(f"main.plugins.{plugin_name}", fromlist=["*"])
            logger.info(f"✅ 成功导入插件: {plugin_name}")
            success_count += 1
        except Exception as e:
            logger.error(f"❌ 导入插件 {plugin_name} 失败: {e}")
    
    logger.info(f"\n插件导入测试结果: {success_count}/{len(plugins_to_test)} 个成功")
    return success_count == len(plugins_to_test)

def test_message_commands_plugin():
    """测试message_commands插件"""
    logger.info("\n=== 测试message_commands插件 ===")
    
    try:
        from main.plugins.message_handler import MessageHandlerPlugin
        from main.core.base_plugin import plugin_registry
        
        # 尝试创建插件实例
        plugin = MessageHandlerPlugin()
        logger.info("✅ 成功创建MessageHandler插件实例")
        
        # 检查插件是否有name属性
        if hasattr(plugin, "name"):
            logger.info(f"✅ 插件name属性: {plugin.name}")
        else:
            logger.error("❌ 插件缺少name属性")
            return False
        
        # 检查插件方法
        required_methods = ["on_load", "on_unload", "get_help_text"]
        for method in required_methods:
            if hasattr(plugin, method):
                logger.info(f"✅ 插件有{method}方法")
            else:
                logger.error(f"❌ 插件缺少{method}方法")
                return False
        
        logger.info("✅ message_commands插件测试通过")
        return True
    except Exception as e:
        logger.error(f"❌ message_commands插件测试失败: {e}")
        return False

def test_session_commands_plugin():
    """测试session_commands插件"""
    logger.info("\n=== 测试session_commands插件 ===")
    
    try:
        from main.plugins.session_commands import SessionPlugin
        
        # 尝试创建插件实例
        plugin = SessionPlugin()
        logger.info("✅ 成功创建SessionPlugin插件实例")
        
        # 检查插件方法
        required_methods = ["on_load", "on_unload", "get_help_text"]
        for method in required_methods:
            if hasattr(plugin, method):
                logger.info(f"✅ 插件有{method}方法")
            else:
                logger.error(f"❌ 插件缺少{method}方法")
                return False
        
        logger.info("✅ session_commands插件测试通过")
        return True
    except Exception as e:
        logger.error(f"❌ session_commands插件测试失败: {e}")
        return False

def test_plugin_registry():
    """测试插件注册表"""
    logger.info("\n=== 测试插件注册表 ===")
    
    try:
        from main.core.base_plugin import plugin_registry
        
        # 检查插件注册表方法
        required_methods = ["register", "unregister", "get_plugin", "list_plugins"]
        for method in required_methods:
            if hasattr(plugin_registry, method):
                logger.info(f"✅ 插件注册表有{method}方法")
            else:
                logger.error(f"❌ 插件注册表缺少{method}方法")
                return False
        
        logger.info("✅ 插件注册表测试通过")
        return True
    except Exception as e:
        logger.error(f"❌ 插件注册表测试失败: {e}")
        return False

def main():
    """主测试函数"""
    logger.info("🔍 开始TG-Content-Bot-Pro插件系统测试")
    
    tests = [
        ("插件导入测试", test_plugin_imports),
        ("message_commands插件测试", test_message_commands_plugin),
        ("session_commands插件测试", test_session_commands_plugin),
        ("插件注册表测试", test_plugin_registry)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 运行: {test_name}")
        try:
            if test_func():
                logger.info(f"✅ {test_name} 通过")
                passed_tests += 1
            else:
                logger.error(f"❌ {test_name} 失败")
        except Exception as e:
            logger.error(f"❌ {test_name} 执行错误: {e}")
    
    logger.info(f"\n📊 测试结果: {passed_tests}/{total_tests} 个测试通过")
    
    if passed_tests == total_tests:
        logger.info("🎉 所有测试通过！插件系统正常工作")
        return 0
    else:
        logger.error("💥 部分测试失败！插件系统存在问题")
        return 1

if __name__ == "__main__":
    sys.exit(main())
