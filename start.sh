#!/bin/bash
# TG-Content-Bot-Pro 启动脚本（简化版）
# 使用示例：
# 前台运行: ./start.sh
# 后台运行: nohup ./start.sh > logs/bot.log 2>&1 &
# 查看最新日志: ls -t logs/ | head -1 | xargs -I{} tail -f logs/{}

set -e

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 日志目录与简单日志轮转（50MB）
mkdir -p logs
manage_logs() {
  local log_file="logs/bot.log"
  local max_size_bytes=$((50 * 1024 * 1024))
  if [ -f "$log_file" ]; then
    local sz=$(stat -c%s "$log_file" 2>/dev/null || stat -f%z "$log_file" 2>/dev/null || echo 0)
    if [ "$sz" -gt "$max_size_bytes" ]; then
      local backup="logs/bot_$(date +%Y%m%d_%H%M%S).log"
      mv "$log_file" "$backup"
      ls -t logs/bot_*.log 2>/dev/null | tail -n +6 | xargs -r rm -f
    fi
  fi
}

# 加载 .env（若存在）
if [ -f ".env" ]; then
  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ $line =~ ^[[:space:]]*# ]] && continue
    [[ -z "${line// }" ]] && continue
    if [[ $line == *"="* ]]; then
      var_name="${line%%=*}"
      var_value="${line#*=}"
      var_name=$(echo "$var_name" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
      var_value=$(echo "$var_value" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
      export "$var_name"="$var_value"
    fi
  done < ".env"
fi

# 启动前检测GitHub新版本（仅提示，不自动拉取）
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
    echo "⚠️ 无法连接远程仓库，跳过版本检测"
  fi
fi

# 激活虚拟环境（如存在）
if [ -f "venv/bin/activate" ]; then
  source venv/bin/activate
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🤖 TG-Content-Bot-Pro 启动脚本"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

manage_logs
python3 -m main
