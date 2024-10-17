#!/bin/bash

# 设置变量
VENV_PATH="/home/API/fiance_backend/.venv"
PROJECT_PATH="/home/API/fiance_backend"
UVICORN_CMD="uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2"

# 激活虚拟环境
source "$VENV_PATH/bin/activate"

# 检查虚拟环境是否成功激活
if [ $? -ne 0 ]; then
    echo "错误：无法激活虚拟环境。请检查路径是否正确。"
    exit 1
fi

# 进入项目目录
cd "$PROJECT_PATH"

# 检查是否成功进入项目目录
if [ $? -ne 0 ]; then
    echo "错误：无法进入项目目录。请检查路径是否正确。"
    exit 1
fi

# 运行uvicorn命令
if command -v uvicorn &> /dev/null
then
    $UVICORN_CMD
else
    echo "错误：uvicorn 命令未找到。请确保它已在虚拟环境中安装。"
    echo "尝试运行: pip install uvicorn"
    exit 1
fi

# 退出虚拟环境
deactivate
