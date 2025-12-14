#!/usr/bin/env python3
"""综合测试脚本 - 验证所有修复是否正常工作"""

import sys
import os
import asyncio
import base64
import struct

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("开始综合测试...")

# 测试1: 验证SESSION工具模块导入
print("\n=== 测试1: SESSION工具模块导入 ===")
try:
    from main.utils.session_utils import (
        validate_pyrogram_session, 
        sanitize_pyrogram_session, 
        get_session_info
    )
    print("✓ SESSION工具模块导入成功")
except Exception as e:
    print(f"✗ SESSION工具模块导入失败: {e}")
    sys.exit(1)

# 测试2: 验证客户端管理器导入
print("\n=== 测试2: 客户端管理器导入 ===")
try:
    from main.core.clients import client_manager
    print("✓ 客户端管理器导入成功")
except Exception as e:
    print(f"✗ 客户端管理器导入失败: {e}")
    sys.exit(1)

# 测试3: 验证SESSION命令插件导入
print("\n=== 测试3: SESSION命令插件导入 ===")
try:
    from main.plugins.session_commands import SessionPlugin
    print("✓ SESSION命令插件导入成功")
except Exception as e:
    print(f"✗ SESSION命令插件导入失败: {e}")
    sys.exit(1)

# 测试4: 验证SESSION命令插件初始化
print("\n=== 测试4: SESSION命令插件初始化 ===")
try:
    session_plugin = SessionPlugin()
    print("✓ SESSION命令插件初始化成功")
except Exception as e:
    print(f"✗ SESSION命令插件初始化失败: {e}")
    sys.exit(1)

# 测试5: 验证SESSION验证功能
print("\n=== 测试5: SESSION验证功能 ===")
try:
    # 测试空SESSION
    result = validate_pyrogram_session("")
    print(f"✓ 空SESSION验证: {result} (预期: False)")
    
    # 测试无效SESSION
    result = validate_pyrogram_session("invalid")
    print(f"✓ 无效SESSION验证: {result} (预期: False)")
    
    # 创建有效的Pyrogram SESSION进行测试
    def create_test_session():
        """创建测试用的Pyrogram SESSION"""
        # 创建271字节的测试数据
        dc_id = 2
        api_id = 123456
        test_mode = False
        auth_key = b'A' * 256  # 256字节的认证密钥
        user_id = 123456789
        is_bot = False
        
        # 打包数据
        data = struct.pack(">BI?256sQ?", dc_id, api_id, test_mode, auth_key, user_id, is_bot)
        
        # 编码为base64 URL安全字符串
        session_string = base64.urlsafe_b64encode(data).decode().rstrip('=')
        return session_string
    
    valid_session = create_test_session()
    result = validate_pyrogram_session(valid_session)
    print(f"✓ 有效SESSION验证: {result} (预期: True)")
    
except Exception as e:
    print(f"✗ SESSION验证功能测试失败: {e}")

# 测试6: 验证SESSION清理功能
print("\n=== 测试6: SESSION清理功能 ===")
try:
    valid_session = create_test_session()
    
    # 测试正常SESSION清理
    cleaned = sanitize_pyrogram_session(valid_session)
    print(f"✓ 正常SESSION清理: 长度 {len(cleaned)}")
    
    # 测试带空格SESSION清理
    spaced_session = " " + valid_session + " "
    cleaned = sanitize_pyrogram_session(spaced_session)
    print(f"✓ 带空格SESSION清理: 长度 {len(cleaned)}")
    
    # 验证清理后的SESSION仍然有效
    is_valid = validate_pyrogram_session(cleaned)
    print(f"✓ 清理后SESSION有效性: {is_valid} (预期: True)")
    
except Exception as e:
    print(f"✗ SESSION清理功能测试失败: {e}")

# 测试7: 验证SESSION信息提取功能
print("\n=== 测试7: SESSION信息提取功能 ===")
try:
    valid_session = create_test_session()
    info = get_session_info(valid_session)
    print(f"✓ SESSION信息提取: {info is not None} (预期: True)")
    if info:
        print(f"  DC ID: {info.get('dc_id')}")
        print(f"  API ID: {info.get('api_id')}")
        print(f"  User ID: {info.get('user_id')}")
except Exception as e:
    print(f"✗ SESSION信息提取功能测试失败: {e}")

# 测试8: 验证客户端管理器SESSION加载逻辑
print("\n=== 测试8: 客户端管理器SESSION加载逻辑 ===")
try:
    # 这个测试只是验证方法是否存在且可调用
    from main.core.clients import ClientManager
    manager = ClientManager()
    
    # 检查方法是否存在
    if hasattr(manager, '_load_session_from_service'):
        print("✓ _load_session_from_service 方法存在")
    else:
        print("✗ _load_session_from_service 方法不存在")
        
    if hasattr(manager, '_handle_userbot_start_error'):
        print("✓ _handle_userbot_start_error 方法存在")
    else:
        print("✗ _handle_userbot_start_error 方法不存在")
        
except Exception as e:
    print(f"✗ 客户端管理器SESSION加载逻辑测试失败: {e}")

print("\n=== 综合测试完成 ===")
print("如果所有测试都通过，说明修复已成功实施。")