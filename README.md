# gpt
> 使用langchain框架搭建一个简易的rag的问答聊天系统

前端：vue3

后端：fastapi

## 代码运行

1. git clone项目到本地

2. 在根目录创建 .env，添加open api 密钥: `OPENAI_API_KEY=sk-h84... ` 

3. 运行前端代码

   1. 调整`/frontend/src/utils/request.js`中的`baseURL`为开发环境`'host': 'localhost'`和`CHROMA = {'host': 'localhost', 'port': 9786}`
   1. `cd frontend`   
   2. `pnpm install`

4. 运行后端代码

   1. 调整`/backend/app/config.py`中的`baseURL`为开发环境`http://127.0.0.1:7979`
   1. `cd backend`
   2. `poetry install`
   3. `poetry shell`
   4. `docker run -d --name chromadb-container -p 9786:8000 -v C:/Users/tangk/Desktop/gpt/backend/app/static/chroma-data:/chroma/chroma -e ANONYMIZED_TELEMETRY=False chromadb/chroma`
   5. 进入mysql，创建一个名为`gpt`空数据库，
      1. `mysql -uroot -p`
      2. `create database gpt charset utf8;`
   7. 使用aerich迁移工具构建数据库表结构
      1. `cd app`

      2. `aerich init -t server.TORTOISE_ORM`  

         `PS`：也需要进入`server.py` 里面的 `TORTOISE_ORM` 修改连接 `mysql` 密码

      3. `aerich init-db`
   8. `cd ./app` 需要进入`app`文件夹里面，`static`目录会创建到`app`下，而不是`backend`下
   9. `python ./server.py` (前面已经进入`poetry shell`)

   ## 打包部署

   1. 前端打包
      1. 调整`/frontend/src/utils/request.js`中的`baseURL`为生产环境`/api`
      1. `pnpm build`
      3. 复制`frontend/dist`文件夹下面所有内容到`docker-volumes/nginx/html`
      4. 同时也准备`nginx.conf`
   2. 打包后端python运行环境

      1. `poetry build`

         生成backend/dist/

         - `langserve_app-0.1.0-py3-none-any.whl`
         - `langserve_app-0.1.0.tar.gz`

         `PS`：pip install 其中任意一个都可以安装运行环境
   3. docker部署
      1. 调整`/app/config.js` :	`开发环境` → `生产环境`

         1. `'host': 'mysql', # 生产环境`
         1. `CHROMA = {'host': 'chroma', 'port': 8000} # 生产环境`

      1. 调用`docker build -t gpt .` 

         1-2步骤是通过`Dockerfile`打包后端为名为`gpt` 的`image`（最耗时间）

      1. `MySQL`表结构处理方式：

         1. 因为数据库使用的是`ORM`，可以在创建docker应用以后，**手动**进入`fastapi`后端容器中，通过前面的命令行`aerich`工具创建表结构（之后手动）
         1. 进入开发环境的数据库，通过`mysqldump -u root -p --no-data --create-options --databases gpt > init.sql` 导出创建数据库、创建表，放进`docker-compose.yml`对应数据库初始化目录里（之前自动）

      1. `docker-compose up`

         通过 `docker-compose.yml` 文件启动整个应用栈，使用到上面自定义`image`：`gpt`,公开的`image`：`nginx`、`mysql`、`chroma`