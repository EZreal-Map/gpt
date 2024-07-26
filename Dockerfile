FROM python:3.11-slim

# 创建 sources.list 文件并添加镜像源
RUN echo "deb http://mirrors.ustc.edu.cn/debian/ bookworm main contrib non-free" > /etc/apt/sources.list && \
    echo "deb-src http://mirrors.ustc.edu.cn/debian/ bookworm main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.ustc.edu.cn/debian-security bookworm-security main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb-src http://mirrors.ustc.edu.cn/debian-security bookworm-security main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.ustc.edu.cn/debian/ bookworm-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb-src http://mirrors.ustc.edu.cn/debian/ bookworm-updates main contrib non-free" >> /etc/apt/sources.list

# 安装支持 C++11 的编译器,清理缓存并移除不再需要的包
RUN apt-get update && \
    apt-get install -y g++ && \
    apt-get clean && \
    apt-get autoremove -y

WORKDIR /backend

# 复制应用文件
COPY ./backend ./

# 安装项目依赖
RUN pip install ./dist/langserve_app-0.1.0-py3-none-any.whl

# 复制应用文件
COPY ./backend/app ./app

# 暴露端口
EXPOSE 7979

# 启动应用
CMD ["python", "./app/server.py"]

# # 安装 poetry
# RUN pip install poetry==1.8.3

# # 安装项目依赖
# RUN poetry install


# # 暴露端口
# EXPOSE 7979

# # 使用 poetry 运行应用
# CMD ["poetry", "run", "python", "./app/server.py"]