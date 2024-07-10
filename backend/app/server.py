#!/usr/bin/env python
from fastapi import FastAPI
from dotenv import load_dotenv
from routers.chat import chat_router
from tortoise.contrib.fastapi import register_tortoise
from config import settings
from routers.retrieval import retrieval_router
from routers.dataset import dataset_router
from routers.appset import appset_router
from fastapi.middleware.cors import CORSMiddleware

# 加载 .env 文件中的环境变量
load_dotenv()

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple api server using Langchain's Runnable interfaces",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)
TORTOISE_ORM = settings.TORTOISE_ORM  # 数据库配置 aerich init -t main.TORTOISE_ORM
register_tortoise(
    app,
    config = TORTOISE_ORM,
    # generate_schemas=True,  # 如果数据库为空，则自动生成对应表单，生产环境不要开
    # add_exception_handlers=True,  # 生产环境不要开，会泄露调试信息
)

app.include_router(chat_router, prefix="/chat")

# 知识库 有关路由
app.include_router(retrieval_router, prefix="/retrieval")
app.include_router(dataset_router, prefix="/dataset")
# 应用 有关路由
app.include_router(appset_router, prefix="/appset")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=7979, reload=True)
    # poetry run langchain serve --port=7979 --host="0.0.0.0"
    # langchain serve --port=7979 --host="0.0.0.0"

    # poetry run python server.py