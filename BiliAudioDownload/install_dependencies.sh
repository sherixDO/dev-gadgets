#!/bin/bash

echo "正在安装Bilibili下载器所需的Python库..."

# 检查pip是否可用
if ! command -v pip &> /dev/null; then
    echo "错误：pip未找到。请先安装Python和pip。"
    exit 1
fi

# 安装依赖
echo "安装requests库..."
pip install requests

echo "安装tqdm库（进度条显示）..."
pip install tqdm

echo "安装mutagen库（MP3元数据处理）..."
pip install mutagen

echo "所有依赖安装完成！"
echo ""
echo "现在你可以运行下载器了："
echo "python downloader.py"
