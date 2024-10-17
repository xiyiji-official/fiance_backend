#!/bin/bash

# 检查是否以root权限运行
if [ "$EUID" -ne 0 ]; then
  echo "请以root权限运行此脚本"
  exit 1
fi

# 设置服务名称和文件
SERVICE_NAME="fastapi@server"
SERVICE_FILE="$(dirname "$0")/fastapi@server.service"
DEST_FILE="/usr/lib/systemd/system/${SERVICE_NAME}.service"
PROJECT_DIR="$(dirname "$0")"
VENV_DIR="$PROJECT_DIR/.venv"
REQUIREMENTS_FILE="$PROJECT_DIR/requirements.txt"

# 检查服务文件是否存在
if [ ! -f "$SERVICE_FILE" ]; then
  echo "错误: 服务文件 $SERVICE_FILE 不存在"
  exit 1
fi

# 检查requirements.txt是否存在
if [ ! -f "$REQUIREMENTS_FILE" ]; then
  echo "错误: requirements.txt 文件不存在"
  exit 1
fi

# 创建虚拟环境
echo "创建虚拟环境..."
python3 -m venv "$VENV_DIR"

# 激活虚拟环境
source "$VENV_DIR/bin/activate"

# 安装依赖
echo "安装依赖..."
pip install -r "$REQUIREMENTS_FILE"

# 退出虚拟环境
deactivate

# 检查目标文件是否已存在
if [ -f "$DEST_FILE" ]; then
  echo "警告: 服务文件 $DEST_FILE 已存在"
  read -p "是否要覆盖? (y/n): " -n 1 -r
  echo    # 移动到新行
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "操作已取消"
    exit 1
  fi
fi

# 复制服务文件到systemd目录
cp "$SERVICE_FILE" "$DEST_FILE"

# 重新加载systemd配置
systemctl daemon-reload

# 检查服务是否已启用
if systemctl is-enabled --quiet "$SERVICE_NAME"; then
  echo "服务 $SERVICE_NAME 已经启用"
else
  read -p "是否要启用服务? (y/n): " -n 1 -r
  echo    # 移动到新行
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    systemctl enable "$SERVICE_NAME"
    echo "服务 $SERVICE_NAME 已启用"
  else
    echo "服务 $SERVICE_NAME 未启用"
  fi
fi

echo "服务 $SERVICE_NAME 已成功添加到systemd"
echo "虚拟环境已创建并安装了依赖"
echo "您可以使用以下命令来管理服务:"
echo "启动服务: sudo systemctl start $SERVICE_NAME"
echo "停止服务: sudo systemctl stop $SERVICE_NAME"
echo "重启服务: sudo systemctl restart $SERVICE_NAME"
echo "查看服务状态: sudo systemctl status $SERVICE_NAME"