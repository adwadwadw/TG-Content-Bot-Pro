#!/usr/bin/env python3
"""MongoDB连接测试脚本"""

import sys
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 从.env文件读取MongoDB连接字符串
def get_mongo_uri():
    """从.env文件获取MongoDB URI"""
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('MONGO_DB='):
                    return line.strip().split('=', 1)[1]
    except Exception as e:
        print(f"读取.env文件失败: {e}")
        return None

def test_mongo_connection():
    """测试MongoDB连接"""
    print("开始测试MongoDB连接...")
    
    # 获取MongoDB URI
    mongo_uri = get_mongo_uri()
    if not mongo_uri:
        print("✗ 无法获取MongoDB连接字符串")
        return False
        
    print(f"MongoDB URI: {mongo_uri[:50]}...")  # 只显示前50个字符以保护隐私
    
    try:
        # 创建MongoDB客户端
        print("正在连接MongoDB...")
        client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=10000,  # 10秒超时
            connectTimeoutMS=10000,
            socketTimeoutMS=30000
        )
        
        # 测试连接
        print("测试连接...")
        client.admin.command('ping')
        print("✓ MongoDB连接成功!")
        
        # 列出数据库
        print("获取数据库列表...")
        db_list = client.list_database_names()
        print(f"✓ 可访问的数据库: {db_list}")
        
        # 关闭连接
        client.close()
        print("✓ 连接测试完成")
        return True
        
    except ServerSelectionTimeoutError as e:
        print(f"✗ MongoDB连接超时: {e}")
        return False
    except ConnectionFailure as e:
        print(f"✗ MongoDB连接失败: {e}")
        return False
    except Exception as e:
        print(f"✗ MongoDB测试出错: {e}")
        return False

if __name__ == "__main__":
    success = test_mongo_connection()
    if success:
        print("\n🎉 MongoDB连接测试通过!")
    else:
        print("\n💥 MongoDB连接测试失败!")
        sys.exit(1)