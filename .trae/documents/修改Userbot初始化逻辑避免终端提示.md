## 修改计划

### 1. 修改 `_init_userbot` 方法
- 确保在没有有效SESSION时，不会调用`await self.userbot.start()`
- 或者确保`start()`方法不会在终端提示输入

### 2. 优化SESSION验证逻辑
- 增强SESSION验证，确保只有有效的SESSION才会被用于启动Userbot
- 避免使用无效SESSION尝试启动Userbot

### 3. 测试修改后的配置
- 运行`python -m main`命令，测试机器人是否能够在没有有效SESSION的情况下正常启动
- 确保不会在终端提示输入手机号
- 测试机器人内部的SESSION生成功能是否正常工作

## 预期结果
- 机器人能够正常启动，不会在终端提示输入手机号
- 能够通过机器人内部命令（如/generatesession）生成和添加SESSION
- Userbot客户端只有在有有效SESSION时才会启动
- 不会出现终端输入提示