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
      2. `create database fastapi charset utf8;`
   6. 使用aerich迁移工具构建数据库表结构
      1. `cd app`
      2. `aerich init -t server.TORTOISE_ORM`
      3. `aerich init-db`
   7. `python ./app/server.py` (前面已经进入`poetry shell`)

   ## 打包部署

   1. 前端打包
      1. 调整`/frontend/src/utils/request.js`中的`baseURL`为生产环境`/api`
      1. `pnpm build`
      2. 复制`frontend/dist`文件夹下面所有内容到`docker-volumes/nginx/html`
   2. 后端打包python运行环境
      1. `poetry build`
   3. docker部署
      1. 调整`/frontend/src/utils/request.js`中的`baseURL`为开发环境`'host': 'localhost'`和`CHROMA = {'host': 'localhost', 'port': 9786}`
      1. `docker-compose up`