#!/usr/bin/env python
from fastapi import FastAPI, Depends
from routers.chat import chat_router
from tortoise.contrib.fastapi import register_tortoise
from config import settings
from routers.retrieval import retrieval_router
from routers.dataset import dataset_router
from routers.appset import appset_router
from routers.appset_no_auth import appset_router_no_auth
from routers.chatset import chatset_router
from routers.chat_history import chat_history_router
from routers.user import user_router
from fastapi.middleware.cors import CORSMiddleware
from utils.authenticate import get_current_user
from dotenv import load_dotenv

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
    config=TORTOISE_ORM,
    # generate_schemas=True,  # 如果数据库为空，则自动生成对应表单，生产环境不要开
    # add_exception_handlers=True,  # 生产环境不要开，会泄露调试信息
)

# 聊天响应 有关路由
app.include_router(chat_router, prefix="/chat")
# 知识库 有关路由
app.include_router(
    retrieval_router, prefix="/retrieval", dependencies=[Depends(get_current_user)]
)
app.include_router(
    dataset_router, prefix="/dataset", dependencies=[Depends(get_current_user)]
)
# 应用 有关路由
app.include_router(
    appset_router, prefix="/appset", dependencies=[Depends(get_current_user)]
)
app.include_router(
    appset_router_no_auth, prefix="/appset"
)  # 将此路由包含在主应用中，不包含全局依赖项
# 聊天记录 有关路由
app.include_router(chatset_router, prefix="/chatset")
app.include_router(chat_history_router, prefix="/chat_history")
# 用户 有关路由
app.include_router(user_router)
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=7979, reload=True)
    # poetry run langchain serve --port=7979 --host="0.0.0.0"
    # langchain serve --port=7979 --host="0.0.0.0"

    # poetry run python server.py
