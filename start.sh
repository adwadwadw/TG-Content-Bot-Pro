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
    local lock_file="logs/bot.lock"
    
    # 检查PID文件是否存在
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "✅ 机器人正在运行 (PID: $pid)"
            return 0
        else
            echo "❌ PID文件存在但进程未运行，清理PID文件"
            rm -f "$pid_file"
            if [ -f "$lock_file" ]; then
                rm -f "$lock_file"
            fi
            return 1
        fi
    fi
    
    # 检查锁定文件是否存在
    if [ -f "$lock_file" ]; then
        local lock_pid=$(cat "$lock_file" 2>/dev/null || echo "")
        if [ -n "$lock_pid" ] && ps -p "$lock_pid" > /dev/null 2>&1; then
            echo "✅ 机器人正在运行 (锁定PID: $lock_pid)"
            return 0
        else
            echo "❌ 锁定文件存在但进程未运行，清理锁定文件"
            rm -f "$lock_file"
            return 1
        fi
    fi
    
    # 检查是否有Python进程在运行
    local python_pids=$(pgrep -f "python.*main" 2>/dev/null || echo "")
    if [ -n "$python_pids" ]; then
        for pid in $python_pids; do
            # 检查进程是否在当前目录下运行
            local proc_cwd=$(readlink /proc/$pid/cwd 2>/dev/null || echo "")
            if [ "$proc_cwd" = "$SCRIPT_DIR" ] || [ "$proc_cwd" = "$(realpath $SCRIPT_DIR)" ]; then
                echo "✅ 机器人正在运行 (PID: $pid)"
                # 更新PID文件
                echo "$pid" > "$pid_file"
                return 0
            fi
        done
    fi
    
    echo "❌ 机器人未运行"
    return 1
}

# 停止进程
stop_bot() {
    local pid_file="logs/bot.pid"
    local lock_file="logs/bot.lock"
    
    # 首先停止当前进程
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
            rm -f "$lock_file"
            echo "✅ 机器人已停止"
        else
            echo "⚠️  PID文件存在但进程未运行，清理PID文件"
            rm -f "$pid_file"
            rm -f "$lock_file"
        fi
    else
        echo "⚠️  未找到运行中的机器人进程"
    fi
    
    # 清理任何残留的锁定文件
    if [ -f "$lock_file" ]; then
        rm -f "$lock_file"
        echo "🧹 清理残留锁定文件"
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
    
    # 启动前检测GitHub新版本
    if command -v git >/dev/null 2>&1; then
        echo "🔍 正在检测GitHub新版本..."
        if git fetch origin main >/dev/null 2>&1; then
            LOCAL_REV=$(git rev-parse HEAD 2>/dev/null || echo "")
            REMOTE_REV=$(git rev-parse origin/main 2>/dev/null || echo "")
            if [ -n "$LOCAL_REV" ] && [ -n "$REMOTE_REV" ] && [ "$LOCAL_REV" != "$REMOTE_REV" ]; then
                echo "📢 检测到仓库有新版本，5秒后继续运行程序..."
                sleep 5
            else
                echo "✅ 当前已是最新版本"
            fi
        else
            echo "⚠️ 远程仓库不可用，跳过版本检测"
        fi
    fi
    
    # 创建启动锁定文件
    local lock_file="logs/bot.lock"
    echo "$" > "$lock_file"
    
    # 清理函数 - 确保锁定文件被删除
    cleanup_lock() {
        if [ -f "$lock_file" ]; then
            rm -f "$lock_file"
        fi
    }
    trap cleanup_lock EXIT
    
    # 如果是后台模式，尽量降低前台输出并跳过前置检测
    if [ "$run_mode" != "background" ]; then
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
    
    if [ "$run_mode" != "background" ]; then
        if python /tmp/test_mongo.py 2>&1 | grep -q "SUCCESS"; then
            echo "✅ 数据库连接成功"
            rm -f /tmp/test_mongo.py
        else
            echo "❌ 数据库连接失败"
            echo "请检查 MONGO_DB 配置是否正确"
            rm -f /tmp/test_mongo.py
            exit 1
        fi
    fi
    
    # 根据运行模式启动
    if [ "$run_mode" = "background" ]; then
        # 后台模式：不输出Python日志到前台，仅最少提示
        manage_logs
        
        if [ -f "venv/bin/activate" ]; then
            nohup bash -c "cd '$SCRIPT_DIR' && source venv/bin/activate && python3 -m main" > logs/bot.log 2>&1 &
        else
            nohup bash -c "cd '$SCRIPT_DIR' && python3 -m main" > logs/bot.log 2>&1 &
        fi
        local pid=$!
        echo "$pid" > logs/bot.pid
        echo "✅ 已在后台启动 (PID: $pid)。查看日志: ls -t logs/ && tail -f logs/最新文件"
        exit 0
    else
        echo ""
        echo "🚀 启动机器人..."
        echo ""
        
        # 管理日志文件
        manage_logs
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

# 日志管理函数
manage_logs() {
    local logs_dir="logs"
    local log_file="logs/bot.log"
    local max_size_mb=50
    local max_size_bytes=$((max_size_mb * 1024 * 1024))
    
    # 创建日志目录
    mkdir -p "$logs_dir"
    
    # 检查日志文件是否存在且超过大小限制
    if [ -f "$log_file" ]; then
        local current_size=$(stat -f%z "$log_file" 2>/dev/null || stat -c%s "$log_file" 2>/dev/null || echo 0)
        
        if [ "$current_size" -gt "$max_size_bytes" ]; then
            echo "📊 日志文件过大 (${current_size} bytes)，进行清理..."
            
            # 创建日志备份
            local backup_file="logs/bot_$(date +%Y%m%d_%H%M%S).log"
            mv "$log_file" "$backup_file"
            echo "✅ 日志已备份到: $backup_file"
            
            # 清理旧的日志文件，只保留最近的5个
            echo "🧹 清理旧日志文件..."
            ls -t logs/bot_*.log 2>/dev/null | tail -n +6 | xargs -r rm -f
        fi
    fi
}

# 设置信号处理
trap cleanup EXIT

# 先处理快捷命令，避免进入主流程
if [[ "$1" == "--status" || "$1" == "-s" ]]; then
    check_status
    exit $?
fi
if [[ "$1" == "--kill" || "$1" == "-k" ]]; then
    stop_bot
    exit 0
fi

# 执行主程序
main "$@"
