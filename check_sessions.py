#!/usr/bin/env python3
"""检查数据库中的SESSION数据"""

import sys
import os
import asyncio

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main.config import settings
from main.core.database import db_manager
from main.services.session_service import session_service

async def check_sessions():
    """检查SESSION数据"""
    print("正在检查数据库中的SESSION数据...")
    
    try:
        # 检查数据库连接
        if db_manager.db is None:
            print("数据库未连接")
            return
            
        print("数据库连接正常")
        
        # 获取所有授权用户
        auth_users = settings.get_auth_users()
        print(f"授权用户: {auth_users}")
        
        # 检查每个授权用户的SESSION
        for user_id in auth_users:
            print(f"\n检查用户 {user_id} 的SESSION:")
            
            # 直接从数据库获取SESSION
            try:
                user = db_manager.db.users.find_one({"user_id": user_id})
                if user and user.get("session_string"):
                    session_str = user["session_string"]
                    print(f"  数据库中的SESSION长度: {len(session_str)} 字符")
                    print(f"  SESSION前10个字符: {session_str[:10] if len(session_str) > 10 else session_str}")
                    
                    # 检查是否是加密的
                    if session_str.startswith(("1", "2", "3")):
                        print("  SESSION看起来是Pyrogram格式")
                    else:
                        print("  SESSION可能已加密或格式不正确")
                else:
                    print(f"  用户 {user_id} 没有SESSION")
            except Exception as e:
                print(f"  检查用户SESSION时出错: {e}")
        
        # 获取所有SESSION
        print("\n获取所有SESSION:")
        try:
            all_sessions = await session_service.get_all_sessions()
            print(f"找到 {len(all_sessions)} 个SESSION")
            for session in all_sessions:
                user_id = session.get("user_id")
                session_str = session.get("session_string", "")
                print(f"  用户 {user_id}: SESSION长度 {len(session_str)} 字符")
        except Exception as e:
            print(f"获取所有SESSION时出错: {e}")
            
    except Exception as e:
        print(f"检查SESSION时出错: {e}")

if __name__ == "__main__":
    asyncio.run(check_sessions())