#!/usr/bin/env python3
"""数据库清理和重置工具"""

import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main.core.database import db_manager
from main.config import settings

def check_invalid_records() -> Dict[str, List[Dict[str, Any]]]:
    """检查数据库中的无效或过期记录"""
    print("🔍 检查数据库中的无效或过期记录...")
    
    invalid_records = {
        "invalid_sessions": [],
        "expired_batches": [],
        "orphaned_messages": [],
        "duplicate_users": []
    }
    
    try:
        if not db_manager.is_connected():
            print("❌ 数据库未连接")
            return invalid_records
            
        # 检查无效的SESSION记录
        print("  检查无效SESSION记录...")
        users_with_sessions = list(db_manager.db.users.find({"session_string": {"$ne": None}}))
        for user in users_with_sessions:
            session = user.get("session_string", "")
            # 检查SESSION是否为空或明显无效
            if not session or len(session) < 10:
                invalid_records["invalid_sessions"].append({
                    "user_id": user["user_id"],
                    "session_length": len(session) if session else 0
                })
        
        # 检查过期的批量任务（超过7天未完成的任务）
        print("  检查过期批量任务...")
        week_ago = datetime.now() - timedelta(days=7)
        expired_batches = list(db_manager.db.batch_tasks.find({
            "start_time": {"$lt": week_ago},
            "status": {"$in": ["running", "pending"]}
        }))
        for batch in expired_batches:
            invalid_records["expired_batches"].append({
                "task_id": str(batch["_id"]),
                "user_id": batch["user_id"],
                "start_time": batch["start_time"]
            })
        
        # 检查孤立的消息记录（用户不存在的消息）
        print("  检查孤立消息记录...")
        all_users = set(u["user_id"] for u in db_manager.db.users.find({}, {"user_id": 1}))
        messages = list(db_manager.db.message_history.find({}))
        for msg in messages:
            if msg["user_id"] not in all_users:
                invalid_records["orphaned_messages"].append({
                    "message_id": msg.get("message_id"),
                    "user_id": msg["user_id"],
                    "forward_date": msg.get("forward_date")
                })
        
        # 检查重复用户记录
        print("  检查重复用户记录...")
        pipeline = [
            {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
            {"$match": {"count": {"$gt": 1}}}
        ]
        duplicates = list(db_manager.db.users.aggregate(pipeline))
        for dup in duplicates:
            invalid_records["duplicate_users"].append({
                "user_id": dup["_id"],
                "count": dup["count"]
            })
            
        print("✅ 无效记录检查完成")
        return invalid_records
        
    except Exception as e:
        print(f"❌ 检查过程中出错: {e}")
        return invalid_records

def display_invalid_records(invalid_records: Dict[str, List[Dict[str, Any]]]) -> None:
    """显示无效记录详情"""
    print("\n📊 无效记录详情:")
    
    if invalid_records["invalid_sessions"]:
        print(f"\n  ❌ 无效SESSION记录 ({len(invalid_records['invalid_sessions'])} 条):")
        for record in invalid_records["invalid_sessions"]:
            print(f"    用户 {record['user_id']}: SESSION长度 {record['session_length']}")
    
    if invalid_records["expired_batches"]:
        print(f"\n  ⏰ 过期批量任务 ({len(invalid_records['expired_batches'])} 条):")
        for record in invalid_records["expired_batches"]:
            print(f"    任务 {record['task_id'][:8]}: 用户 {record['user_id']}, 开始于 {record['start_time']}")
    
    if invalid_records["orphaned_messages"]:
        print(f"\n  🗑️ 孤立消息记录 ({len(invalid_records['orphaned_messages'])} 条):")
        for record in invalid_records["orphaned_messages"]:
            print(f"    消息 {record['message_id']}: 用户 {record['user_id']}")
    
    if invalid_records["duplicate_users"]:
        print(f"\n  🔁 重复用户记录 ({len(invalid_records['duplicate_users'])} 条):")
        for record in invalid_records["duplicate_users"]:
            print(f"    用户 {record['user_id']}: 出现 {record['count']} 次")

def reset_database() -> bool:
    """重置数据库到初始状态"""
    print("🔄 重置数据库到初始状态...")
    
    try:
        if not db_manager.is_connected():
            print("❌ 数据库未连接")
            return False
            
        # 删除所有集合中的数据
        collections = ["users", "message_history", "batch_tasks", "settings"]
        for collection_name in collections:
            if collection_name in db_manager.db.list_collection_names():
                count = db_manager.db[collection_name].count_documents({})
                db_manager.db[collection_name].delete_many({})
                print(f"  ✅ 清空集合 {collection_name} ({count} 条记录)")
        
        # 重新创建必要的索引
        print("  🔄 重新创建索引...")
        db_manager._create_indexes()
        
        # 添加主用户
        auth_users = settings.get_auth_users()
        for user_id in auth_users:
            db_manager.db.users.insert_one({
                "user_id": user_id,
                "is_authorized": True,
                "is_banned": False,
                "join_date": datetime.now(),
                "total_forwards": 0,
                "total_size": 0,
                "daily_upload": 0,
                "daily_download": 0,
                "monthly_upload": 0,
                "monthly_download": 0,
                "total_upload": 0,
                "total_download": 0,
                "last_reset_daily": datetime.now().date().isoformat(),
                "last_reset_monthly": datetime.now().strftime("%Y-%m")
            })
            print(f"  ✅ 添加主用户 {user_id}")
        
        print("✅ 数据库重置完成")
        return True
        
    except Exception as e:
        print(f"❌ 数据库重置过程中出错: {e}")
        return False

def main():
    """主函数"""
    print("🤖 数据库清理和重置工具")
    print("=" * 50)
    
    # 检查数据库连接
    if not db_manager.is_connected():
        print("❌ 无法连接到数据库")
        return
    
    print("✅ 数据库连接正常")
    
    # 检查是否有DB_RESET环境变量
    db_reset = os.environ.get('DB_RESET', '').lower() in ['true', '1', 'yes']
    
    if db_reset:
        print("\n🔄 检测到 DB_RESET=true，自动执行数据库重置...")
        if reset_database():
            print("\n🎉 数据库重置成功完成")
        else:
            print("\n💥 数据库重置失败")
        return
    
    # 检查无效记录
    invalid_records = check_invalid_records()
    
    # 显示无效记录
    display_invalid_records(invalid_records)
    
    # 统计总数
    total_invalid = sum(len(records) for records in invalid_records.values())
    print(f"\n📈 总共发现 {total_invalid} 条无效记录")
    
    if total_invalid > 0:
        print("\n💡 建议:")
        print("  1. 运行此脚本时设置 DB_RESET=true 来清理所有数据")
        print("  2. 或者手动处理特定的无效记录")
    else:
        print("\n✅ 数据库状态良好，没有发现无效记录")

if __name__ == "__main__":
    main()