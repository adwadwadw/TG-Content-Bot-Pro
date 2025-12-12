#!/bin/bash

# TG消息提取器一键部署脚本 v2.0
# 基于版本85d895a深度优化，增强稳定性、兼容性和自动化程度
# 支持Docker优先部署、智能环境检测、自动故障恢复
# 兼容Linux/macOS/WSL/Git Bash环境，Windows用户建议使用WSL

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# 系统检测和依赖检查
check_system_info() {
    info "检测系统信息..."
    
    # 检测操作系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS_TYPE="Linux"
        log "✓ 操作系统：Linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS_TYPE="macOS"
        log "✓ 操作系统：macOS"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        OS_TYPE="Windows"
        warn "操作系统：Windows（建议使用WSL或Git Bash）"
    else
        OS_TYPE="Unknown"
        warn "未知操作系统类型：$OSTYPE"
    fi
    
    # 检测架构
    ARCH=$(uname -m)
    log "✓ 系统架构：$ARCH"
    
    # 检测内存
    if command -v free &> /dev/null; then
        MEM_AVAILABLE=$(free -m 2>/dev/null | awk '/^Mem:/{print $2}' || echo "unknown")
        log "✓ 可用内存：${MEM_AVAILABLE}MB"
    fi
}

# 检查依赖
check_dependencies() {
    log "检查系统依赖..."
    
    # 检查Docker（支持新版docker compose插件）
    if command -v docker &> /dev/null; then
        DOCKER_AVAILABLE=true
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | tr -d ',')
        log "✓ Docker已安装 (版本: $DOCKER_VERSION)"
        
        # 检查Docker服务状态
        if ! docker info &> /dev/null; then
            warn "Docker守护进程未运行，请启动Docker服务"
            DOCKER_AVAILABLE=false
        fi
    else
        DOCKER_AVAILABLE=false
        warn "Docker未安装，将使用手动部署方式"
    fi
    
    # 检查Docker Compose（兼容新旧版本）
    COMPOSE_AVAILABLE=false
    if command -v docker-compose &> /dev/null; then
        COMPOSE_AVAILABLE=true
        COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | tr -d ',')
        log "✓ Docker Compose已安装 (版本: $COMPOSE_VERSION)"
    elif docker compose version &> /dev/null; then
        COMPOSE_AVAILABLE=true
        COMPOSE_VERSION=$(docker compose version --short)
        log "✓ Docker Compose插件已安装 (版本: $COMPOSE_VERSION)"
    else
        warn "Docker Compose未安装"
    fi
    
    # 检查Python版本和虚拟环境支持
    if command -v python3 &> /dev/null; then
        PYTHON_AVAILABLE=true
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        
        # 检查Python版本是否满足要求
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ $PYTHON_MAJOR -eq 3 ] && [ $PYTHON_MINOR -ge 8 ]; then
            log "✓ Python $PYTHON_VERSION已安装 (满足要求)"
        else
            warn "Python版本 $PYTHON_VERSION 可能过低，建议使用Python 3.8+"
        fi
        
        # 检查venv模块
        if python3 -c "import venv" &> /dev/null; then
            VENV_AVAILABLE=true
            log "✓ Python虚拟环境支持正常"
        else
            VENV_AVAILABLE=false
            warn "Python虚拟环境模块不可用"
        fi
    else
        PYTHON_AVAILABLE=false
        VENV_AVAILABLE=false
        warn "Python3未安装"
    fi
    
    # 检查git
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version | cut -d' ' -f3)
        log "✓ Git已安装 (版本: $GIT_VERSION)"
    else
        error "Git未安装，请先安装Git"
    fi
    
    # 检查curl
    if command -v curl &> /dev/null; then
        log "✓ curl已安装"
    else
        warn "curl未安装，可能影响网络请求"
    fi
}

# 环境变量智能配置
setup_environment() {
    log "配置环境变量..."
    
    # 检查.env文件是否存在且有效
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            success "✓ 已创建.env文件（基于模板）"
        else
            # 创建基本的.env文件模板
            cat > .env << 'EOF'
# TG消息提取器环境配置
# ================================
# 必需配置（必须填写）
API_ID=your_api_id_here
API_HASH=your_api_hash_here
BOT_TOKEN=your_bot_token_here
AUTH=your_user_id_here
MONGO_DB=your_mongodb_connection_string

# 可选配置
SESSION=your_pyrogram_session_string
FORCESUB=your_channel_username
HEALTH_CHECK_PORT=8080

# 代理配置（如需要）
TELEGRAM_PROXY_SCHEME=socks5
TELEGRAM_PROXY_HOST=proxy_host
TELEGRAM_PROXY_PORT=1080
TELEGRAM_PROXY_USERNAME=proxy_user
TELEGRAM_PROXY_PASSWORD=proxy_pass
EOF
            warn "✓ 已创建基础.env文件（请手动配置）"
        fi
    else
        log "✓ .env文件已存在"
    fi
    
    # 显示环境变量配置指南
    show_env_config_guide
    
    # 检查环境变量完整性
    check_required_env_vars
}

# 显示环境变量配置指南
show_env_config_guide() {
    echo ""
    echo "=================================================="
    echo "环境变量配置指南"
    echo "=================================================="
    echo ""
    echo "必需参数（必须填写）："
    echo "1. API_ID: Telegram API ID (从 https://my.telegram.org 获取)"
    echo "2. API_HASH: Telegram API Hash (从 https://my.telegram.org 获取)"
    echo "3. BOT_TOKEN: 机器人Token (从 @BotFather 获取)"
    echo "4. AUTH: 授权用户ID (从 @userinfobot 获取)"
    echo "5. MONGO_DB: MongoDB连接字符串"
    echo ""
    echo "可选参数："
    echo "6. FORCESUB: 强制订阅频道用户名（不带@）"
    echo "7. SESSION: Pyrogram会话字符串（可自动生成）"
    echo "8. HEALTH_CHECK_PORT: 健康检查端口（默认8080）"
    echo "9. TELEGRAM_PROXY_*: 代理配置（如需要）"
    echo ""
    echo "快速获取方式："
    echo "- API_ID/API_HASH: 访问 my.telegram.org"
    echo "- BOT_TOKEN: 在Telegram中搜索 @BotFather"
    echo "- AUTH: 在Telegram中搜索 @userinfobot"
    echo "- MONGO_DB: 注册 MongoDB Atlas 免费集群"
    echo ""
    echo "=================================================="
    
    # 检查是否所有必需变量都已配置
    if ! check_env_vars_complete; then
        echo ""
        read -p "是否现在编辑.env文件？(y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            # 安全地选择编辑器，避免任何未定义变量错误
            local editor_found=false
            
            # 检查可用编辑器（按优先级排序）
            for editor in "${EDITOR:-}" nano vim vi; do
                if [ -n "$editor" ] && command -v "$editor" &> /dev/null; then
                    log "使用编辑器: $editor"
                    "$editor" .env
                    editor_found=true
                    break
                fi
            done
            
            if [ "$editor_found" = "false" ]; then
                warn "未找到可用的文本编辑器，请手动编辑 .env 文件"
                echo ""
                echo "可以使用以下命令手动编辑："
                echo "nano .env    # 简单易用"
                echo "vim .env     # 功能强大"
                echo "vi .env      # 基础编辑器"
                echo ""
                echo "编辑完成后，请重新运行部署脚本："
                echo "./deploy.sh"
            fi
        fi
    fi
}

# 检查环境变量是否完整
check_env_vars_complete() {
    local required_vars=("API_ID" "API_HASH" "BOT_TOKEN" "AUTH" "MONGO_DB")
    local missing_count=0
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" .env 2>/dev/null || grep "^${var}=" .env | grep -q "your_.*_here"; then
            missing_count=$((missing_count + 1))
        fi
    done
    
    [ $missing_count -eq 0 ]
}

# 检查必需的环境变量
check_required_env_vars() {
    log "检查必需环境变量..."
    
    required_vars=("API_ID" "API_HASH" "BOT_TOKEN" "AUTH" "MONGO_DB")
    missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" .env 2>/dev/null || grep "^${var}=" .env | grep -q "your_.*_here"; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        warn "以下必需环境变量未正确配置：${missing_vars[*]}"
        return 1
    else
        success "✓ 所有必需环境变量已正确配置"
        return 0
    fi
}

# Docker部署（增强版）
deploy_with_docker() {
    info "使用Docker部署..."
    
    # 检查Docker可用性
    if [ "$DOCKER_AVAILABLE" != "true" ] || [ "$COMPOSE_AVAILABLE" != "true" ]; then
        error "Docker环境不可用，无法进行Docker部署"
    fi
    
    # 获取docker-compose命令
    local compose_cmd="docker-compose"
    if command -v docker-compose &> /dev/null; then
        compose_cmd="docker-compose"
    elif docker compose version &> /dev/null; then
        compose_cmd="docker compose"
    else
        error "未找到可用的docker-compose命令"
    fi
    
    log "使用命令: $compose_cmd"
    
    # 停止并清理现有容器
    if $compose_cmd ps | grep -q "tg-content-bot"; then
        log "停止现有容器..."
        $compose_cmd down
        sleep 5
    fi
    
    # 检查镜像是否已存在，避免重复构建
    if docker images | grep -q "tg-content-bot"; then
        log "检测到现有镜像，跳过构建..."
    else
        log "构建Docker镜像..."
        if ! $compose_cmd build --no-cache; then
            warn "镜像构建失败，尝试使用缓存构建..."
            $compose_cmd build
        fi
    fi
    
    # 启动容器
    log "启动Docker容器..."
    if ! $compose_cmd up -d; then
        error "容器启动失败"
    fi
    
    # 等待容器启动
    log "等待服务启动..."
    local max_wait=60
    local wait_time=0
    
    while [ $wait_time -lt $max_wait ]; do
        if $compose_cmd ps | grep -q "Up" && $compose_cmd ps | grep -q "healthy"; then
            break
        fi
        
        wait_time=$((wait_time + 5))
        if [ $wait_time -lt $max_wait ]; then
            log "等待容器启动... (${wait_time}s/${max_wait}s)"
            sleep 5
        fi
    done
    
    # 检查服务状态
    if $compose_cmd ps | grep -q "Up"; then
        success "✓ Docker部署成功"
        
        # 显示部署信息
        show_deployment_info "docker"
    else
        error "Docker部署失败，容器未正常运行"
    fi
}

# 手动部署（增强版）
deploy_manually() {
    info "使用手动部署..."
    
    # 检查Python可用性
    if [ "$PYTHON_AVAILABLE" != "true" ]; then
        error "Python环境不可用，无法进行手动部署"
    fi
    
    # 检查Python虚拟环境
    if [ ! -d "venv" ]; then
        log "创建Python虚拟环境..."
        if ! python3 -m venv venv; then
            error "虚拟环境创建失败"
        fi
        success "✓ 虚拟环境创建成功"
    else
        log "✓ 虚拟环境已存在"
    fi
    
    # 激活虚拟环境
    log "激活虚拟环境..."
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
    else
        error "虚拟环境激活文件未找到"
    fi
    
    # 升级pip并安装依赖
    log "安装Python依赖..."
    if ! pip install --upgrade pip; then
        warn "pip升级失败，继续安装依赖..."
    fi
    
    # 分步安装依赖，提高稳定性
    log "安装核心依赖..."
    if ! pip install -r requirements.txt; then
        warn "批量安装失败，尝试分步安装..."
        
        # 分步安装关键依赖
        pip install telethon==1.34.0
        pip install pyrogram==2.0.106
        pip install pymongo==4.6.0
        pip install python-decouple==3.8
        
        # 安装其他依赖
        pip install -r requirements.txt --no-deps || warn "部分依赖安装失败"
    fi
    
    success "✓ Python依赖安装完成"
    
    # 检查start.sh权限
    if [ ! -x "start.sh" ]; then
        log "设置执行权限..."
        chmod +x start.sh
    fi
    
    # 显示部署信息
    show_deployment_info "manual"
    
    # 询问是否立即启动
    echo ""
    read -p "是否现在启动服务？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log "启动机器人服务..."
        ./start.sh
    fi
}

# 显示部署信息
show_deployment_info() {
    local deploy_type=$1
    local port=8080
    
    # 获取健康检查端口
    if [ -f ".env" ] && grep -q "^HEALTH_CHECK_PORT=" .env; then
        port=$(grep "^HEALTH_CHECK_PORT=" .env | cut -d'=' -f2)
    fi
    
    echo ""
    echo "========================================"
    echo "部署成功！"
    echo "========================================"
    
    if [ "$deploy_type" = "docker" ]; then
        echo "部署方式：Docker容器"
        echo "服务状态："
        docker-compose ps 2>/dev/null || docker compose ps 2>/dev/null
        echo ""
        echo "管理命令："
        echo "- 查看日志：docker-compose logs -f"
        echo "- 停止服务：docker-compose down"
        echo "- 重启服务：docker-compose restart"
        echo "- 查看状态：docker-compose ps"
    else
        echo "部署方式：手动部署"
        echo "虚拟环境：venv/"
        echo ""
        echo "管理命令："
        echo "- 启动服务：./start.sh"
        echo "- 或使用：source venv/bin/activate && python3 -m main"
        echo "- 停止服务：Ctrl+C"
        echo "- 重新部署：./deploy.sh"
    fi
    
    echo ""
    echo "监控信息："
    echo "- 健康检查：curl http://localhost:$port/health"
    echo "- 状态页面：http://localhost:$port/"
    echo "- 实时日志：查看上述管理命令"
    echo ""
    echo "快速测试："
    echo "curl -s http://localhost:$port/health | jq . 2>/dev/null || curl -s http://localhost:$port/health"
    echo "========================================"
}

# 健康检查（增强版）
health_check() {
    info "执行健康检查..."
    
    # 获取健康检查端口
    local port=8080
    if [ -f ".env" ] && grep -q "^HEALTH_CHECK_PORT=" .env; then
        port=$(grep "^HEALTH_CHECK_PORT=" .env | cut -d'=' -f2)
    fi
    
    local max_retries=15
    local retry_interval=3
    local retry_count=0
    
    log "健康检查地址：http://localhost:$port/health"
    
    while [ $retry_count -lt $max_retries ]; do
        if [ "$DOCKER_AVAILABLE" = true ] && [ "$COMPOSE_AVAILABLE" = true ]; then
            # Docker健康检查
            if curl -s --max-time 5 --connect-timeout 3 http://localhost:$port/health > /dev/null; then
                # 检查详细健康状态
                local health_response=$(curl -s http://localhost:$port/health)
                if echo "$health_response" | grep -q '"status":"healthy"' || echo "$health_response" | grep -q 'healthy'; then
                    success "✓ 健康检查通过 - 服务运行正常"
                    echo "响应信息：$health_response"
                    return 0
                fi
            fi
        else
            # 手动部署健康检查
            if pgrep -f "python3 -m main" > /dev/null || pgrep -f "./start.sh" > /dev/null; then
                # 尝试HTTP健康检查
                if curl -s --max-time 5 http://localhost:$port/health > /dev/null; then
                    success "✓ 服务进程正常运行"
                    return 0
                else
                    log "✓ 服务进程运行中（HTTP接口未响应）"
                    return 0
                fi
            fi
        fi
        
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $max_retries ]; then
            log "健康检查失败，${retry_interval}秒后重试... ($retry_count/$max_retries)"
            sleep $retry_interval
        fi
    done
    
    warn "健康检查失败，请检查服务状态"
    
    # 提供故障排查建议
    echo ""
    echo "故障排查："
    if [ "$DOCKER_AVAILABLE" = true ] && [ "$COMPOSE_AVAILABLE" = true ]; then
        echo "1. 查看容器日志：docker-compose logs -f"
        echo "2. 检查容器状态：docker-compose ps"
        echo "3. 重启服务：docker-compose restart"
    else
        echo "1. 检查Python进程：ps aux | grep python"
        echo "2. 查看应用日志：检查控制台输出"
        echo "3. 检查端口占用：netstat -tlnp | grep $port"
    fi
    echo "4. 验证环境变量：cat .env | grep -v '^#'"
    echo ""
    
    return 1
}

# 自动克隆项目（增强版）
auto_clone_project() {
    local project_dir="TG-Content-Bot-Pro"
    local current_dir=$(pwd)
    
    # 检查是否已经在项目根目录
    if [ -f "README.md" ] && [ -f "docker-compose.yml" ] && [ -f "deploy.sh" ]; then
        log "✓ 当前已在项目根目录: $current_dir"
        return 0
    fi
    
    info "检测到当前目录不是项目根目录，准备自动处理..."
    
    # 检查是否在项目子目录中
    if [ -f "../README.md" ] && [ -f "../docker-compose.yml" ]; then
        log "检测到项目根目录在上级目录..."
        cd ..
        log "✓ 切换到项目根目录: $(pwd)"
        return 0
    fi
    
    # 检查项目目录是否已存在
    if [ -d "$project_dir" ]; then
        log "项目目录已存在，切换到项目目录..."
        cd "$project_dir"
        
        # 验证目录内容
        if [ -f "README.md" ] && [ -f "docker-compose.yml" ]; then
            log "✓ 项目目录验证成功: $(pwd)"
            return 0
        else
            warn "项目目录存在但内容不完整，重新克隆..."
            cd ..
            rm -rf "$project_dir"
        fi
    fi
    
    # 克隆项目
    info "开始克隆项目..."
    log "项目地址: https://github.com/liwoyuandiane/TG-Content-Bot-Pro.git"
    
    # 检查网络连接
    if ! curl -s --connect-timeout 5 https://github.com > /dev/null; then
        error "网络连接失败，请检查网络设置"
    fi
    
    # 克隆项目（支持多种方式）
    if git clone https://github.com/liwoyuandiane/TG-Content-Bot-Pro.git "$project_dir"; then
        success "✓ 项目克隆成功"
        cd "$project_dir"
        
        # 验证克隆结果
        if [ -f "README.md" ] && [ -f "docker-compose.yml" ] && [ -f "deploy.sh" ]; then
            log "✓ 项目文件验证成功"
            log "✓ 当前目录: $(pwd)"
            return 0
        else
            error "项目克隆不完整，请手动检查"
        fi
    else
        # 尝试使用备用方式
        warn "标准克隆失败，尝试备用方式..."
        
        if curl -sL https://github.com/liwoyuandiane/TG-Content-Bot-Pro/archive/main.tar.gz | tar xz; then
            mv TG-Content-Bot-Pro-main "$project_dir"
            cd "$project_dir"
            success "✓ 备用方式克隆成功"
        else
            error "项目克隆失败，请检查网络连接和Git配置"
        fi
    fi
    
    # 最终验证
    if [ ! -f "README.md" ] || [ ! -f "docker-compose.yml" ]; then
        error "无法定位到项目根目录，请手动检查"
    fi
}

# 显示欢迎信息
show_welcome() {
    echo ""
    echo "========================================"
    echo "🚀 TG消息提取器一键部署脚本 v2.0"
    echo "========================================"
    echo ""
    echo "📋 功能特性："
    echo "- 智能环境检测和依赖检查"
    echo "- Docker优先部署（推荐）"
    echo "- 手动部署备用方案"
    echo "- 自动故障恢复和重试机制"
    echo "- 详细的状态监控和健康检查"
    echo ""
    echo "⚙️  部署方式："
    echo "1. Docker部署 - 容器化，隔离性好"
    echo "2. 手动部署 - 直接运行，灵活性高"
    echo ""
    echo "📝 环境要求："
    echo "- 操作系统: Linux/macOS/Windows(WSL)"
    echo "- 内存: 建议1GB+"
    echo "- 网络: 可访问GitHub和Telegram API"
    echo "========================================"
    echo ""
}

# 智能选择部署方式
smart_deploy_selection() {
    info "智能选择最优部署方式..."
    
    # 根据环境条件智能推荐
    if [ "$DOCKER_AVAILABLE" = "true" ] && [ "$COMPOSE_AVAILABLE" = "true" ]; then
        log "✓ Docker环境完整可用"
        
        # 检查内存是否充足（Docker需要更多内存）
        if [ "$MEM_AVAILABLE" != "unknown" ] && [ $MEM_AVAILABLE -lt 1024 ]; then
            warn "系统内存较低(${MEM_AVAILABLE}MB)，建议使用手动部署"
            echo ""
            read -p "是否继续使用Docker部署？(y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                deploy_manually
                return
            fi
        fi
        
        deploy_with_docker
    else
        if [ "$PYTHON_AVAILABLE" = "true" ] && [ "$VENV_AVAILABLE" = "true" ]; then
            log "✓ Python环境可用，使用手动部署"
            deploy_manually
        else
            error "没有可用的部署环境，请安装Docker或Python"
        fi
    fi
    
    # 执行健康检查
    health_check
}

# 主函数
main() {
    show_welcome
    
    # 系统检测
    check_system_info
    
    # 自动克隆或切换到项目目录
    auto_clone_project
    
    # 检查依赖
    check_dependencies
    
    # 配置环境变量
    setup_environment
    
    # 检查环境变量是否完整
    if ! check_required_env_vars; then
        warn "环境变量配置不完整，部署可能失败"
        echo ""
        read -p "是否继续部署？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            info "部署已取消，请先配置环境变量"
            exit 0
        fi
    fi
    
    # 选择部署方式
    echo ""
    echo "请选择部署方式："
    echo "1) Docker部署（推荐） - 容器化，易于管理"
    echo "2) 手动部署 - 直接运行，资源占用少"
    echo "3) 智能选择 - 根据系统环境自动选择"
    echo ""
    
    read -p "请输入选择 (1/2/3，默认3): " choice
    choice=${choice:-3}
    
    case $choice in
        1)
            if [ "$DOCKER_AVAILABLE" = "true" ] && [ "$COMPOSE_AVAILABLE" = "true" ]; then
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
        3)
            smart_deploy_selection
            ;;
        *)
            error "无效选择"
            ;;
    esac
    
    success "部署完成！"
    
    # 显示后续操作指南
    echo ""
    echo "========================================"
    echo "🎉 部署成功！后续操作指南"
    echo "========================================"
    echo ""
    echo "📊 监控服务："
    echo "- 实时日志：查看上述管理命令"
    echo "- 健康状态：curl http://localhost:8080/health"
    echo "- 系统状态：查看状态页面"
    echo ""
    echo "🛠️  管理命令："
    echo "- 重启服务：重新运行此脚本"
    echo "- 更新代码：git pull && ./deploy.sh"
    echo "- 查看帮助：./deploy.sh --help"
    echo ""
    echo "🔧 故障排查："
    echo "- 检查日志文件"
    echo "- 验证环境变量"
    echo "- 查看系统资源"
    echo "========================================"
    echo ""
}

# 显示详细帮助信息
show_help() {
    echo ""
    echo "========================================"
    echo "TG消息提取器一键部署脚本 - 使用说明"
    echo "========================================"
    echo ""
    echo "📖 基本用法："
    echo "  ./deploy.sh                   交互式部署（推荐）"
    echo "  bash <(curl -sL https://raw.githubusercontent.com/liwoyuandiane/TG-Content-Bot-Pro/main/deploy.sh)"
    echo ""
    echo "⚙️  命令行参数："
    echo "  --help, -h                   显示此帮助信息"
    echo "  docker                       强制使用Docker部署"
    echo "  manual                       强制使用手动部署"
    echo "  auto                         智能选择部署方式"
    echo "  health                       执行健康检查"
    echo "  update                       更新项目代码并重新部署"
    echo "  status                       查看服务状态"
    echo "  clean                        清理部署环境"
    echo ""
    echo "🔧 高级功能："
    echo "  --env-file=FILE              指定环境变量文件"
    echo "  --port=PORT                  指定健康检查端口"
    echo "  --no-health-check            跳过健康检查"
    echo "  --force                      强制重新部署"
    echo ""
    echo "📋 示例："
    echo "  # 一键部署（推荐）"
    echo "  ./deploy.sh"
    echo ""
    echo "  # 强制Docker部署"
    echo "  ./deploy.sh docker"
    echo ""
    echo "  # 指定环境变量文件"
    echo "  ./deploy.sh --env-file=my-config.env"
    echo ""
    echo "  # 更新项目"
    echo "  ./deploy.sh update"
    echo "========================================"
    echo ""
    exit 0
}

# 更新项目
update_project() {
    info "更新项目代码..."
    
    # 检查是否在Git仓库中
    if [ ! -d ".git" ]; then
        error "当前目录不是Git仓库，无法更新"
    fi
    
    # 拉取最新代码
    if git pull origin main; then
        success "✓ 代码更新成功"
        
        # 询问是否重新部署
        echo ""
        read -p "是否重新部署？(Y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Nn]$ ]]; then
            info "更新完成，未重新部署"
            exit 0
        fi
        
        # 重新部署
        exec "$0" "${@:2}"
    else
        error "代码更新失败"
    fi
}

# 查看服务状态
check_status() {
    info "检查服务状态..."
    
    # 检查Docker服务状态
    if [ "$DOCKER_AVAILABLE" = "true" ] && [ "$COMPOSE_AVAILABLE" = "true" ]; then
        if docker-compose ps 2>/dev/null || docker compose ps 2>/dev/null; then
            echo ""
            health_check
        else
            warn "Docker服务未运行"
        fi
    else
        # 检查Python进程
        if pgrep -f "python3 -m main" > /dev/null || pgrep -f "./start.sh" > /dev/null; then
            success "✓ 服务进程运行中"
            health_check
        else
            warn "服务进程未运行"
        fi
    fi
}

# 清理部署环境
clean_environment() {
    warn "清理部署环境..."
    
    echo "此操作将："
    echo "- 停止并删除Docker容器（如果存在）"
    echo "- 删除虚拟环境（如果存在）"
    echo "- 保留.env配置文件"
    echo ""
    
    read -p "确认清理？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        info "清理已取消"
        exit 0
    fi
    
    # 清理Docker环境
    if [ "$DOCKER_AVAILABLE" = "true" ] && [ "$COMPOSE_AVAILABLE" = "true" ]; then
        log "清理Docker环境..."
        docker-compose down 2>/dev/null || docker compose down 2>/dev/null
        docker system prune -f 2>/dev/null || true
    fi
    
    # 清理虚拟环境
    if [ -d "venv" ]; then
        log "删除虚拟环境..."
        rm -rf venv
    fi
    
    success "✓ 环境清理完成"
}

# 处理命令行参数
case "${1:-}" in
    "--help" | "-h")
        show_help
        ;;
    "docker")
        check_system_info
        check_dependencies
        setup_environment
        if [ "$DOCKER_AVAILABLE" = "true" ] && [ "$COMPOSE_AVAILABLE" = "true" ]; then
            deploy_with_docker
            health_check
        else
            error "Docker不可用，无法强制使用Docker部署"
        fi
        ;;
    "manual")
        check_system_info
        check_dependencies
        setup_environment
        deploy_manually
        ;;
    "auto")
        check_system_info
        check_dependencies
        setup_environment
        smart_deploy_selection
        ;;
    "health")
        check_system_info
        check_dependencies
        health_check
        ;;
    "update")
        update_project
        ;;
    "status")
        check_system_info
        check_dependencies
        check_status
        ;;
    "clean")
        clean_environment
        ;;
    "")
        main
        ;;
    *)
        # 处理带参数的情况
        case "$1" in
            --env-file=*)
                ENV_FILE="${1#*=}"
                if [ -f "$ENV_FILE" ]; then
                    cp "$ENV_FILE" .env
                    info "使用自定义环境变量文件: $ENV_FILE"
                else
                    error "环境变量文件不存在: $ENV_FILE"
                fi
                main
                ;;
            --port=*)
                PORT="${1#*=}"
                export HEALTH_CHECK_PORT="$PORT"
                info "设置健康检查端口: $PORT"
                main
                ;;
            --no-health-check)
                NO_HEALTH_CHECK=true
                info "跳过健康检查"
                main
                ;;
            --force)
                FORCE_DEPLOY=true
                info "强制重新部署"
                main
                ;;
            *)
                error "未知参数: $1，使用 --help 查看帮助"
                ;;
        esac
        ;;
esac