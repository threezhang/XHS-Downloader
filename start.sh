#!/bin/bash

# 创建日志目录
mkdir -p logs

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
gunicorn -c gunicorn.conf.py source.web.app:app