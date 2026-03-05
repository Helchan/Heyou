#!/bin/bash

# 获取脚本所在目录的绝对路径，并切换到该目录
cd "$(dirname "$0")"

# 尝试寻找 Homebrew 安装的 Python 3 (通常自带兼容的 Tkinter)
# 优先检查 Apple Silicon Mac 的 Homebrew 路径
if [ -x "/opt/homebrew/bin/python3" ]; then
    PYTHON_CMD="/opt/homebrew/bin/python3"
# 其次检查 Intel Mac 的 Homebrew 路径
elif [ -x "/usr/local/bin/python3" ]; then
    PYTHON_CMD="/usr/local/bin/python3"
# 最后尝试系统路径中的 python3
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "错误：未找到 Python 3。"
    echo "请尝试运行 'brew install python' 安装最新版 Python。"
    read -n 1 -s
    exit 1
fi

echo "使用 Python: $PYTHON_CMD"

# 运行主程序
"$PYTHON_CMD" main.py

# 检查退出代码
if [ $? -ne 0 ]; then
    echo ""
    echo "程序异常退出。"
    echo "如果是 'macOS 13 required' 错误，请尝试升级 macOS 或安装最新版 Python："
    echo "brew install python"
fi

echo ""
echo "程序已退出，按任意键关闭..."
read -n 1 -s
