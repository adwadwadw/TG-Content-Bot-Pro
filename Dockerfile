# 使用GitHub Actions构建的镜像
FROM ghcr.io/liwoyuandiane/TG-Content-Bot-Pro:latest

# 启动命令（继承自基础镜像）
CMD ["python3", "-m", "main"]
