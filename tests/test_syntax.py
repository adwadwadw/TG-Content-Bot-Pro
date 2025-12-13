#!/usr/bin/env python3
"""
插件语法测试脚本
直接测试插件文件的语法和基本结构，不依赖配置加载
"""
import sys
import os
import logging
import ast
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_file_syntax(file_path):
    """测试文件语法是否正确"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f"语法错误: {e}"
    except Exception as e:
        return False, f"其他错误: {e}"

def test_plugin_structure(file_path):
    """测试插件基本结构是否符合要求"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否导入了BasePlugin
        if 'from ..core.base_plugin import BasePlugin' not in content and 'from main.core.base_plugin import BasePlugin' not in content:
            return False, "未导入BasePlugin"
        
        # 检查是否定义了插件类
        if 'class ' not in content:
            return False, "未定义插件类"
        
        # 检查是否有on_load和on_unload方法
        if 'async def on_load' not in content:
            return False, "缺少on_load方法"
        if 'async def on_unload' not in content:
            return False, "缺少on_unload方法"
        
        # 检查是否有插件实例化和注册代码
        if 'plugin_registry.register' not in content and '_plugin_registry.register' not in content:
            return False, "缺少插件注册代码"
        
        return True, None
    except Exception as e:
        return False, f"结构检查错误: {e}"

def main():
    """主测试函数"""
    logger.info("🔍 开始TG-Content-Bot-Pro插件语法测试")
    
    plugins_dir = Path("main/plugins")
    plugin_files = list(plugins_dir.glob("*.py"))
    plugin_files = [f for f in plugin_files if f.name != "__init__.py"]
    
    if not plugin_files:
        logger.error("❌ 未找到插件文件")
        return 1
    
    logger.info(f"📁 找到 {len(plugin_files)} 个插件文件")
    
    passed_syntax = 0
    passed_structure = 0
    total_files = len(plugin_files)
    
    for plugin_file in plugin_files:
        plugin_name = plugin_file.stem
        logger.info(f"\n📋 测试: {plugin_name}")
        
        # 测试语法
        syntax_ok, syntax_err = test_file_syntax(plugin_file)
        if syntax_ok:
            logger.info(f"✅ 语法检查通过")
            passed_syntax += 1
        else:
            logger.error(f"❌ 语法检查失败: {syntax_err}")
        
        # 测试结构
        structure_ok, structure_err = test_plugin_structure(plugin_file)
        if structure_ok:
            logger.info(f"✅ 结构检查通过")
            passed_structure += 1
        else:
            logger.error(f"❌ 结构检查失败: {structure_err}")
    
    logger.info(f"\n📊 测试结果:")
    logger.info(f"语法检查: {passed_syntax}/{total_files} 通过")
    logger.info(f"结构检查: {passed_structure}/{total_files} 通过")
    
    if passed_syntax == total_files and passed_structure == total_files:
        logger.info("🎉 所有测试通过！插件系统语法和结构正确")
        return 0
    else:
        logger.error("💥 部分测试失败！请检查插件文件")
        return 1

if __name__ == "__main__":
    sys.exit(main())
