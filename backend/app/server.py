#!/usr/bin/env python
from fastapi import FastAPI, Depends
from routers.chat import chat_router
from tortoise.contrib.fastapi import register_tortoise
from config import settings
from routers.retrieval import retrieval_router
from routers.dataset import dataset_router
from routers.appset import appset_router
from routers.chatset import chatset_router
from routers.chat_history import chat_history_router
from routers.admin_user import admin_user_router
from routers.fileset import fileset_router, clear_unmatched_filesets
from routers.audio import audio_router
from routers.normal_user import normal_user_router
from fastapi.middleware.cors import CORSMiddleware
from utils.authenticate import (
    get_current_admin_user_dependence,
    get_current_normal_user_dependence,
)
from apscheduler.schedulers.asyncio import (
    AsyncIOScheduler,
)  # 定时任务, 用于清除临时文件
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

scheduler = AsyncIOScheduler()  # 创建定时任务

# 聊天响应 有关路由
app.include_router(chat_router, prefix="/chat")
# 知识库 有关路由
app.include_router(
    retrieval_router,
    prefix="/retrieval",
    dependencies=[Depends(get_current_admin_user_dependence)],
)
app.include_router(
    dataset_router,
    prefix="/dataset",
    dependencies=[Depends(get_current_admin_user_dependence)],
)
# 应用 有关路由
app.include_router(
    appset_router,
    prefix="/appset",
    dependencies=[Depends(get_current_normal_user_dependence)],
)

# 聊天记录 有关路由
app.include_router(
    chatset_router,
    prefix="/chatset",
    dependencies=[Depends(get_current_normal_user_dependence)],
)
app.include_router(
    chat_history_router,
    prefix="/chat_history",
    dependencies=[Depends(get_current_normal_user_dependence)],
)
# admin用户 有关路由（这个路由特殊，不能添加身份验证）
app.include_router(admin_user_router)
# fileset存储 有关路由
app.include_router(
    fileset_router,
    prefix="/fileset",
    dependencies=[Depends(get_current_normal_user_dependence)],
)
# 语音识别，语音生成 有关路由（因为audio合成与识别都用到WebSocket，而jwt token技术是基于HTTP，所以不能添加身份验证）
app.include_router(audio_router)
# 普通用户 有关路由
app.include_router(
    normal_user_router, dependencies=[Depends(get_current_normal_user_dependence)]
)


# 增加清除临时文件定时任务
@app.on_event("startup")
async def startup_event():
    scheduler.add_job(clear_unmatched_filesets, "cron", hour=4)  # 每天凌晨4点运行
    scheduler.start()
    print("Scheduler：定时清除临时FileSet已启动")
    await clear_unmatched_filesets()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=7979, reload=True)
