FROM python:3.11-slim

# 创建 sources.list 文件并添加镜像源
RUN echo "deb http://mirrors.ustc.edu.cn/debian/ bookworm main contrib non-free" > /etc/apt/sources.list && \
    echo "deb-src http://mirrors.ustc.edu.cn/debian/ bookworm main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.ustc.edu.cn/debian-security bookworm-security main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb-src http://mirrors.ustc.edu.cn/debian-security bookworm-security main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.ustc.edu.cn/debian/ bookworm-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb-src http://mirrors.ustc.edu.cn/debian/ bookworm-updates main contrib non-free" >> /etc/apt/sources.list

# 安装必要的开发工具和 portaudio 库
RUN apt-get update && \
    apt-get install -y \
    g++ \
    portaudio19-dev \
    gcc \
    && apt-get clean && \
    apt-get autoremove -y

WORKDIR /home/backend

# 复制配置打包文件
COPY ./backend/dist ./dist

# 安装项目依赖
RUN pip install ./dist/langserve_app-0.1.0-py3-none-any.whl

# 复制源代码文件
COPY ./backend/app ./app

# 暴露端口
EXPOSE 7979

# 启动应用
CMD ["sh", "-c", "cd ./app && python ./server.py"]