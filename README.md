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
3. 配置 QQ 邮箱：
   - 登录您的 QQ 邮箱
   - 开启 SMTP 服务
   - 获取授权码
   - 将授权码填入 `mempool_monitor.py` 中的 `SMTP_PASSWORD` 变量

## 使用方法

1. 修改 `mempool_monitor.py` 中的邮箱配置：
   - 将 `SMTP_PASSWORD` 替换为您的 QQ 邮箱授权码
   - 如需修改目标区块高度，修改 `TARGET_BLOCK_HEIGHT` 的值

2. 运行脚本：
   ```bash
   python mempool_monitor.py
   ```

## 注意事项

- 请确保您的网络连接稳定
- 建议使用 screen 或 nohup 等工具在后台运行脚本
- 邮件发送使用 QQ 邮箱的 SMTP 服务，请确保已开启相关服务 