from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langserve import add_routes
from fastapi import APIRouter, Request
from itertools import count
from sse_starlette import EventSourceResponse
from pydantic import BaseModel
import json

from dotenv import load_dotenv
# 加载 .env 文件中的环境变量
load_dotenv()
chat_router = APIRouter()

model = ChatOpenAI(model="gpt-3.5-turbo")

prompt = ChatPromptTemplate.from_template("tell me a joke about {topic}")
add_routes(
    chat_router,
    prompt | model,
    path="/joke",
)


# 使用 itertools 的 count 函数来生成自增的 id
id_counter = count()

# 定义生成器函数以流式发送数据
async def chat_streamer(request: Request, query: str = "what color is the sky?"):
    async for chunk in model.astream(query):
        print(chunk)
        if await request.is_disconnected():
            print("连接已中断")
            break
        id = next(id_counter)  # 获取下一个自增的 id
        data = json.dumps({"content": chunk.content, "id": chunk.id}, ensure_ascii=False)
        yield {"data": data, "event": "message", "id": id}


class QueryModel(BaseModel):
    query: str

# 创建一个FastAPI路由来处理流式响应
@chat_router.post("/")
async def chat(request: Request, query_body: QueryModel):
    return EventSourceResponse(chat_streamer(request, query=query_body.query))