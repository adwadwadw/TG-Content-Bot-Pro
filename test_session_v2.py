#!/usr/bin/env python3
"""测试Pyrogram v2.0 SESSION字符串兼容性"""

import asyncio
import logging
import re
from pyrogram import Client

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 测试SESSION字符串（请替换为您的实际SESSION）
TEST_SESSION = "AQFLdDsAoNEgx7GkfCB8BRFszIePuNFzaIcCg6Noz5nvaaJL84NLDt4PSd9UX5hOyCc72bZs4ULQR6YQRyIi0Ebu9aqvNXukaZsRjscGY5d2stsf3hImuG5zs0gjFIgFWfFr5EdjoMeqfT4G7Tss3ymBBg9qyh7YnN2NjTZmBE57TT0Pg7RDrpUOvOrGJ4irewvf391xh9zvJZhXx7vFNcWidkIKS8DgGo1oYVKqgbn9BHLkZdwscielAZMJCP6VTorPospHiZnShmG6PIVGah8qyPuNcFvWqdqqspx2e8seeb55IVBpoKEvdQXlOiSuZYqMQ0IJNZlEWFBaigAAAAE62fAA"

async def test_session_compatibility():
    """测试SESSION字符串兼容性"""
    logger.info("开始测试Pyrogram v2.0 SESSION字符串兼容性...")
    
    # 清理SESSION字符串
    cleaned_session = re.sub(r'[^A-Za-z0-9+/=]', '', TEST_SESSION)
    logger.info(f"原始SESSION长度: {len(TEST_SESSION)}")
    logger.info(f"清理后SESSION长度: {len(cleaned_session)}")
    
    # 尝试解码SESSION
    try:
        import base64
        decoded = base64.b64decode(cleaned_session)
        logger.info(f"SESSION解码成功，解码后长度: {len(decoded)} 字节")
    except Exception as e:
        logger.error(f"SESSION解码失败: {e}")
        return
    
    # 创建客户端测试
    try:
        # 使用清理后的SESSION创建客户端
        client = Client(
            "test_client",
            api_id=123456,  # 替换为实际的API ID
            api_hash="your_api_hash_here",  # 替换为实际的API Hash
            session_string=cleaned_session,
            app_version="Pyrogram 2.0.106",
            device_model="Test Device",
            system_version="Test System",
            lang_code="en"
        )
        
        logger.info("客户端创建成功")
        
        # 尝试连接（注意：这里不会真正连接，因为我们没有有效的API凭证）
        # 但我们可以通过检查SESSION解析是否成功来判断兼容性
        logger.info("Pyrogram v2.0 SESSION字符串格式兼容性测试完成")
        
    except Exception as e:
        logger.error(f"客户端创建失败: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(test_session_compatibility())