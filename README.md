# Mempool 区块高度监控

这个脚本用于监控 mempool.space 的区块高度，当达到指定高度时发送邮件通知。

## 功能特点

- 监控 mempool.space 的区块高度
- 当区块高度达到目标值时发送邮件通知
- 每分钟自动检查一次
- 详细的日志记录

## 使用前准备

1. 安装 Python 3.6 或更高版本
2. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```
3. 配置环境变量：
   - 复制 `config.env.example` 为 `config.env`
   - 在 `config.env` 中填写您的配置信息：
     ```
     # 目标区块高度
     TARGET_BLOCK_HEIGHT=899130

     # 邮件配置
     SMTP_SERVER=smtp.qq.com
     SMTP_PORT=587
     SENDER_EMAIL=your-email@qq.com
     RECEIVER_EMAIL=your-email@qq.com
     SMTP_PASSWORD=your-email-authorization-code
     ```

## 使用方法

1. 确保 `config.env` 文件配置正确
2. 运行脚本：
   ```bash
   python mempool_monitor.py
   ```

## 安全性说明

1. 敏感信息保护：
   - `config.env` 文件包含敏感信息，已被添加到 `.gitignore`
   - 请勿将 `config.env` 文件提交到版本控制系统
   - 在分享代码时，只分享 `config.env.example` 文件

2. 首次提交到 GitHub：
   ```bash
   # 初始化 Git 仓库
   git init
   
   # 添加文件
   git add .
   
   # 提交更改
   git commit -m "Initial commit"
   
   # 添加远程仓库
   git remote add origin your-github-repo-url
   
   # 推送到 GitHub
   git push -u origin main
   ```

3. 检查敏感信息：
   ```bash
   # 检查是否有敏感文件被意外添加
   git status
   
   # 检查 Git 历史中是否包含敏感信息
   git log -p
   ```

## 注意事项

- 请确保您的网络连接稳定
- 建议使用 screen 或 nohup 等工具在后台运行脚本
- 邮件发送使用 QQ 邮箱的 SMTP 服务，请确保已开启相关服务
- 请妥善保管 `config.env` 文件，不要将其提交到版本控制系统
- 如果发现敏感信息被意外提交，请立即更改相关密码和授权码 