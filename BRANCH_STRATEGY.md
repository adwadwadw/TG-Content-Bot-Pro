# 分支策略说明

## 分支结构

### main 分支
- **用途**：开发和构建镜像
- **Dockerfile**：包含完整的构建步骤（从python:3.11-slim开始）
- **GitHub Actions**：自动构建并推送到GitHub Container Registry

### pull 分支  
- **用途**：部署和运行
- **Dockerfile**：直接使用构建好的镜像（ghcr.io/用户名/TG-Content-Bot-Pro:latest）
- **优势**：部署更快，无需重新构建

## 工作流程

### 1. 开发阶段（main分支）
```bash
git checkout main
# 进行代码修改
# 提交并推送
```

GitHub Actions会自动构建镜像并推送到：
`ghcr.io/你的用户名/TG-Content-Bot-Pro:latest`

### 2. 部署阶段（pull分支）
```bash
git checkout pull
docker-compose up -d  # 直接使用预构建的镜像
```

## 分支同步

当main分支有更新时，需要同步到pull分支：

```bash
# 切换到pull分支
git checkout pull

# 合并main分支的更新（除了Dockerfile）
git merge main --no-commit

# 恢复pull分支特有的Dockerfile
git checkout HEAD -- Dockerfile

# 提交合并
git commit -m "Merge main branch updates"
```

## 注意事项

1. **首次使用**：需要先在main分支构建镜像，然后pull分支才能使用
2. **镜像更新**：main分支构建新镜像后，pull分支会自动使用最新版本
3. **用户名替换**：记得将Dockerfile中的"你的用户名"替换为实际GitHub用户名

## 快速部署命令

```bash
# 拉取最新镜像
docker pull ghcr.io/你的用户名/TG-Content-Bot-Pro:latest

# 使用docker-compose部署
docker-compose up -d

# 查看日志
docker-compose logs -f
```