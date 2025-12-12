#!/bin/bash

# TG消息提取器一键部署脚本
# 支持Docker和手动部署两种方式
# 基于版本85d895a优化，增强环境变量处理和健康检查
# 注意：此脚本适用于Linux/macOS环境，Windows用户请使用WSL或Git Bash

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# 检查依赖
check_dependencies() {
    log "检查系统依赖..."
    
    # 检查Docker
    if command -v docker &> /dev/null; then
        DOCKER_AVAILABLE=true
        log "✓ Docker已安装"
    else
        DOCKER_AVAILABLE=false
        warn "Docker未安装，将使用手动部署方式"
    fi
    
    # 检查Docker Compose
    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
        COMPOSE_AVAILABLE=true
        log "✓ Docker Compose已安装"
    else
        COMPOSE_AVAILABLE=false
        warn "Docker Compose未安装"
    fi
    
    # 检查Python
    if command -v python3 &> /dev/null; then
        PYTHON_AVAILABLE=true
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log "✓ Python $PYTHON_VERSION已安装"
    else
        PYTHON_AVAILABLE=false
        warn "Python3未安装"
    fi
    
    # 检查git
    if ! command -v git &> /dev/null; then
        error "Git未安装，请先安装Git"
    fi
    log "✓ Git已安装"
}

# 配置环境变量
setup_environment() {
    log "配置环境变量..."
    
    if [ ! -f ".env" ]; then
        cp .env.example .env
        log "✓ 已创建.env文件"
        
        echo ""
        echo "=================================================="
        echo "请编辑.env文件配置以下必需参数："
        echo "=================================================="
        echo "必需参数："
        echo "1. API_ID: Telegram API ID (从 my.telegram.org 获取)"
        echo "2. API_HASH: Telegram API Hash (从 my.telegram.org 获取)"
        echo "3. BOT_TOKEN: 机器人Token (从 @BotFather 获取)"
        echo "4. AUTH: 授权用户ID (从 @userinfobot 获取)"
        echo "5. MONGO_DB: MongoDB连接字符串"
        echo ""
        echo "可选参数："
        echo "6. FORCESUB: 强制订阅频道用户名（不带@）"
        echo "7. SESSION: Pyrogram会话字符串"
        echo "8. TELEGRAM_PROXY_*: 代理配置（如需要）"
        echo "9. HEALTH_CHECK_PORT: 健康检查端口（默认8080）"
        echo ""
        echo "使用命令编辑：nano .env"
        echo "=================================================="
        echo ""
        
        read -p "是否现在编辑.env文件？(y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} .env
        fi
    else
        log "✓ .env文件已存在"
        
        # 检查必需的环境变量是否已配置
        check_required_env_vars
    fi
}

# 检查必需的环境变量
check_required_env_vars() {
    log "检查必需环境变量..."
    
    required_vars=("API_ID" "API_HASH" "BOT_TOKEN" "AUTH" "MONGO_DB")
    missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" .env 2>/dev/null; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        warn "以下必需环境变量未配置：${missing_vars[*]}"
        echo ""
        read -p "是否现在编辑.env文件？(y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} .env
        fi
    else
        log "✓ 所有必需环境变量已配置"
    fi
}

# Docker部署
deploy_with_docker() {
    log "使用Docker部署..."
    
    # 停止并删除现有容器
    if docker-compose ps | grep -q "tg-content-bot-pro"; then
        log "停止现有容器..."
        docker-compose down
    fi
    
    # 构建并启动容器
    log "启动Docker容器..."
    docker-compose up -d
    
    # 等待容器启动
    log "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    if docker-compose ps | grep -q "Up"; then
        log "✓ Docker部署成功"
        
        # 显示健康检查信息
        echo ""
        echo "========================================"
        echo "部署成功！"
        echo "========================================"
        echo "服务状态："
        docker-compose ps
        echo ""
        echo "查看日志：docker-compose logs -f"
        echo "停止服务：docker-compose down"
        echo "重启服务：docker-compose restart"
        echo "健康检查：curl http://localhost:8080/health"
        echo "========================================"
    else
        error "Docker部署失败，请检查日志"
    fi
}

# 手动部署
deploy_manually() {
    log "使用手动部署..."
    
    # 检查Python虚拟环境
    if [ ! -d "venv" ]; then
        log "创建Python虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    log "激活虚拟环境..."
    source venv/bin/activate
    
    # 安装依赖
    log "安装Python依赖..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # 启动服务
    log "启动机器人服务..."
    
    # 检查start.sh权限
    if [ ! -x "start.sh" ]; then
        chmod +x start.sh
    fi
    
    echo ""
    echo "========================================"
    echo "手动部署完成！"
    echo "========================================"
    echo "启动服务：./start.sh"
    echo "或使用：python3 -m main"
    echo "健康检查：curl http://localhost:8080/health"
    echo "========================================"
    echo ""
    
    read -p "是否现在启动服务？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ./start.sh
    fi
}

# 健康检查
health_check() {
    log "执行健康检查..."
    
    # 获取健康检查端口
    local port=8080
    if [ -f ".env" ] && grep -q "^HEALTH_CHECK_PORT=" .env; then
        port=$(grep "^HEALTH_CHECK_PORT=" .env | cut -d'=' -f2)
    fi
    
    local max_retries=10
    local retry_interval=5
    local retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        if [ "$DOCKER_AVAILABLE" = true ] && [ "$COMPOSE_AVAILABLE" = true ]; then
            # Docker健康检查
            if curl -s --max-time 10 http://localhost:$port/health > /dev/null; then
                log "✓ 健康检查通过"
                echo "服务状态：正常运行"
                echo "健康检查地址：http://localhost:$port/health"
                echo "状态页面：http://localhost:$port/"
                echo "日志查看：docker-compose logs -f"
                return 0
            fi
        else
            # 手动部署健康检查
            if pgrep -f "python3 -m main" > /dev/null || pgrep -f "./start.sh" > /dev/null; then
                log "✓ 服务进程正常运行"
                echo "服务状态：进程运行中"
                echo "健康检查：请手动访问 http://localhost:$port/health"
                return 0
            fi
        fi
        
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $max_retries ]; then
            log "健康检查失败，${retry_interval}秒后重试... ($retry_count/$max_retries)"
            sleep $retry_interval
        fi
    done
    
    warn "健康检查失败，请检查服务状态"
    echo "检查日志："
    if [ "$DOCKER_AVAILABLE" = true ] && [ "$COMPOSE_AVAILABLE" = true ]; then
        echo "docker-compose logs -f"
    else
        echo "查看控制台输出或系统日志"
    fi
    return 1
}

# 自动克隆项目
auto_clone_project() {
    local project_dir="TG-Content-Bot-Pro"
    
    # 如果当前目录不是项目根目录，自动克隆
    if [ ! -f "README.md" ] || [ ! -f "docker-compose.yml" ]; then
        log "检测到当前目录不是项目根目录，自动克隆项目..."
        
        # 检查是否已经克隆过
        if [ -d "$project_dir" ]; then
            log "项目目录已存在，切换到项目目录..."
            cd "$project_dir"
        else
            # 克隆项目
            if git clone https://github.com/liwoyuandiane/TG-Content-Bot-Pro.git "$project_dir"; then
                log "✓ 项目克隆成功"
                cd "$project_dir"
            else
                error "项目克隆失败，请检查网络连接"
            fi
        fi
    fi
    
    # 再次确认是否在项目根目录
    if [ ! -f "README.md" ] || [ ! -f "docker-compose.yml" ]; then
        error "无法定位到项目根目录，请手动检查"
    fi
    
    log "✓ 当前目录：$(pwd)"
}

# 主函数
main() {
    echo ""
    echo "========================================"
    echo "TG消息提取器一键部署脚本"
    echo "========================================"
    echo ""
    
    # 自动克隆或切换到项目目录
    auto_clone_project
    
    # 检查依赖
    check_dependencies
    
    # 配置环境变量
    setup_environment
    
    # 选择部署方式
    echo ""
    echo "请选择部署方式："
    echo "1) Docker部署（推荐）"
    echo "2) 手动部署"
    echo ""
    
    read -p "请输入选择 (1/2): " choice
    
    case $choice in
        1)
            if [ "$DOCKER_AVAILABLE" = true ] && [ "$COMPOSE_AVAILABLE" = true ]; then
                deploy_with_docker
                health_check
            else
                warn "Docker不可用，切换到手动部署"
                deploy_manually
            fi
            ;;
        2)
            deploy_manually
            ;;
        *)
            error "无效选择"
            ;;
    esac
    
    echo ""
    log "部署完成！"
    echo ""
    echo "后续操作："
    echo "- 查看日志：docker-compose logs -f (Docker) 或 查看控制台输出 (手动)"
    echo "- 停止服务：docker-compose down (Docker) 或 Ctrl+C (手动)"
    echo "- 更新代码：git pull && ./deploy.sh"
    echo ""
}

# 处理命令行参数
case "${1:-}" in
    "--help" | "-h")
        echo "使用说明："
        echo "  ./deploy.sh          交互式部署"
        echo "  ./deploy.sh docker   强制使用Docker部署"
        echo "  ./deploy.sh manual   强制使用手动部署"
        echo "  ./deploy.sh health   执行健康检查"
        exit 0
        ;;
    "docker")
        check_dependencies
        setup_environment
        if [ "$DOCKER_AVAILABLE" = true ] && [ "$COMPOSE_AVAILABLE" = true ]; then
            deploy_with_docker
            health_check
        else
            error "Docker不可用，无法强制使用Docker部署"
        fi
        ;;
    "manual")
        check_dependencies
        setup_environment
        deploy_manually
        ;;
    "health")
        health_check
        ;;
    "")
        main
        ;;
    *)
        error "未知参数: $1，使用 --help 查看帮助"
        ;;
esac