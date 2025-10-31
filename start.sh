#!/bin/bash
# TG-Content-Bot-Pro 启动脚本
# 直接运行: ./start.sh
# 后台运行: nohup ./start.sh &
# 查看日志: tail -f logs/bot.log

# 版本信息
SCRIPT_VERSION="2.0.0"

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 切换到脚本目录
cd "$SCRIPT_DIR"

# 创建日志目录
mkdir -p logs

# 检查环境变量
check_env_variables() {
    # 检查必需的环境变量
    missing_vars=()
    
    if [ -z "$API_ID" ] || [ -z "$API_HASH" ]; then
        missing_vars+=("API_ID/API_HASH")
    fi
    
    if [ -z "$BOT_TOKEN" ]; then
        missing_vars+=("BOT_TOKEN")
    fi
    
    if [ -z "$AUTH" ]; then
        missing_vars+=("AUTH")
    fi
    
    if [ -z "$MONGO_DB" ]; then
        missing_vars+=("MONGO_DB")
    fi
    
    # 如果系统环境变量不完整，检查.env文件
    if [ ${#missing_vars[@]} -gt 0 ]; then
        if [ -f ".env" ]; then
            # 逐行读取.env文件
            while IFS= read -r line || [[ -n "$line" ]]; do
                # 跳过注释和空行
                if [[ $line =~ ^[[:space:]]*# ]] || [[ -z "${line// }" ]]; then
                    continue
                fi
                
                # 提取变量名和值
                if [[ $line == *"="* ]]; then
                    var_name="${line%%=*}"
                    var_value="${line#*=}"
                    
                    # 去除变量名和值的前后空格
                    var_name=$(echo "$var_name" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
                    var_value=$(echo "$var_value" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
                    
                    # 导出变量
                    export "$var_name"="$var_value"
                fi
            done < ".env"
            
            # 重新检查环境变量
            missing_vars=()
            if [ -z "$API_ID" ] || [ -z "$API_HASH" ]; then
                missing_vars+=("API_ID/API_HASH")
            fi
            
            if [ -z "$BOT_TOKEN" ]; then
                missing_vars+=("BOT_TOKEN")
            fi
            
            if [ -z "$AUTH" ]; then
                missing_vars+=("AUTH")
            fi
            
            if [ -z "$MONGO_DB" ]; then
                missing_vars+=("MONGO_DB")
            fi
        fi
    fi
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        echo "错误: 缺少必需的环境变量: ${missing_vars[*]}"
        echo "请配置环境变量后重新运行此脚本"
        echo ""
        echo "方式一：创建 .env 文件"
        echo "  cp .env.example .env"
        echo "  nano .env  # 编辑配置"
        echo ""
        echo "方式二：设置系统环境变量"
        echo "  export API_ID=your_api_id"
        echo "  export API_HASH=your_api_hash"
        echo "  export BOT_TOKEN=your_bot_token"
        echo "  export AUTH=your_user_id"
        echo "  export MONGO_DB=your_mongodb_uri"
        return 1
    fi
    
    return 0
}

# 显示帮助信息
show_help() {
    echo "TG-Content-Bot-Pro 启动脚本 v${SCRIPT_VERSION}"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help      显示此帮助信息"
    echo "  -v, --version   显示版本信息"
    echo "  -f, --foreground 前台运行（默认）"
    echo "  -b, --background 后台运行"
    echo "  -s, --status     检查运行状态"
    echo "  -k, --kill       停止运行中的进程"
    echo ""
}

# 显示版本信息
show_version() {
    echo "TG-Content-Bot-Pro 启动脚本 v${SCRIPT_VERSION}"
}

# 检查进程状态
check_status() {
    local pid_file="logs/bot.pid"
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "✅ 机器人正在运行 (PID: $pid)"
            return 0
        else
            echo "❌ PID文件存在但进程未运行，清理PID文件"
            rm -f "$pid_file"
            return 1
        fi
    else
        echo "❌ 机器人未运行"
        return 1
    fi
}

# 停止进程
stop_bot() {
    local pid_file="logs/bot.pid"
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "🛑 正在停止机器人 (PID: $pid)..."
            kill "$pid"
            # 等待进程结束
            local count=0
            while ps -p "$pid" > /dev/null 2>&1 && [ $count -lt 10 ]; do
                sleep 1
                count=$((count + 1))
            done
            
            if ps -p "$pid" > /dev/null 2>&1; then
                echo "⚠️  进程仍在运行，强制终止..."
                kill -9 "$pid"
            fi
            
            rm -f "$pid_file"
            echo "✅ 机器人已停止"
        else
            echo "⚠️  PID文件存在但进程未运行，清理PID文件"
            rm -f "$pid_file"
        fi
    else
        echo "⚠️  未找到运行中的机器人进程"
    fi
}

# 主程序
main() {
    local run_mode="foreground"
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--version)
                show_version
                exit 0
                ;;
            -f|--foreground)
                run_mode="foreground"
                shift
                ;;
            -b|--background)
                run_mode="background"
                shift
                ;;
            -s|--status)
                check_status
                exit $?
                ;;
            -k|--kill)
                stop_bot
                exit 0
                ;;
            *)
                echo "错误: 未知选项 '$1'"
                echo "使用 $0 --help 查看帮助信息"
                exit 1
                ;;
        esac
    done
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🤖 TG-Content-Bot-Pro 启动脚本 v${SCRIPT_VERSION}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "运行模式: $run_mode"
    echo ""
    
    # 检查是否已经在运行
    if check_status > /dev/null 2>&1; then
        echo "⚠️  机器人已经在运行中"
        echo "如果需要重启，请先使用: $0 --kill"
        exit 1
    fi
    
    # 检查环境变量
    if ! check_env_variables; then
        exit 1
    fi
    
    # 激活虚拟环境（如果存在）
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        echo "✅ 虚拟环境已激活"
    else
        echo "⚠️  未找到虚拟环境，使用系统Python"
    fi
    
    # 测试 MongoDB 连接
    echo "🔍 测试数据库连接..."
    cat > /tmp/test_mongo.py << 'EOF_TEST'
import sys
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

mongo_uri = os.getenv('MONGO_DB')
if not mongo_uri:
    print("ERROR: MONGO_DB not set")
    sys.exit(1)

try:
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("SUCCESS")
    sys.exit(0)
except ServerSelectionTimeoutError:
    print("ERROR: Connection timeout")
    sys.exit(1)
except ConnectionFailure as e:
    print(f"ERROR: {e}")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
EOF_TEST
    
    if python /tmp/test_mongo.py 2>&1 | grep -q "SUCCESS"; then
        echo "✅ 数据库连接成功"
        rm -f /tmp/test_mongo.py
    else
        echo "❌ 数据库连接失败"
        echo "请检查 MONGO_DB 配置是否正确"
        rm -f /tmp/test_mongo.py
        exit 1
    fi
    
    echo ""
    echo "🚀 启动机器人..."
    echo ""
    
    # 根据运行模式启动
    if [ "$run_mode" = "background" ]; then
        echo "📱 后台运行模式"
        echo "   日志文件: logs/bot.log"
        echo "   PID文件: logs/bot.pid"
        echo ""
        
        # 后台运行
        nohup python3 -m main > logs/bot.log 2>&1 &
        local pid=$!
        
        # 保存PID
        echo "$pid" > logs/bot.pid
        
        echo "✅ 机器人已启动 (PID: $pid)"
        echo "💡 查看日志: tail -f logs/bot.log"
        echo "💡 检查状态: $0 --status"
        echo "💡 停止运行: $0 --kill"
        echo ""
        
        # 等待几秒检查是否启动成功
        sleep 3
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "✅ 启动成功！"
        else
            echo "❌ 启动失败，请检查日志文件"
            rm -f logs/bot.pid
            exit 1
        fi
    else
        echo "📱 前台运行模式"
        echo "   按 Ctrl+C 停止运行"
        echo ""
        
        # 前台运行
        python3 -m main
    fi
}

# 清理函数
cleanup() {
    echo ""
    echo "🧹 清理临时文件..."
    rm -f /tmp/test_mongo.py
    echo "✅ 清理完成"
}

# 设置信号处理
trap cleanup EXIT

# 执行主程序
main "$@"
