#!/bin/bash

# 进入脚本所在目录
cd "$(dirname "$0")"

# 使用 nohup 在后台运行监控程序
nohup python mempool_monitor.py > mempool.log 2>&1 &

# 显示进程ID
echo "监控程序已在后台启动，进程ID: $!"
echo "日志文件: mempool.log" 