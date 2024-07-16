from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langserve import add_routes
from fastapi import APIRouter, Request
from itertools import count
from sse_starlette import EventSourceResponse
from pydantic import BaseModel, Field
import json
from utils.retrieval import retrieval_similarity_search
from uuid import UUID
from typing import Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.documents import Document
from models.models import APPSet




from dotenv import load_dotenv
# 加载 .env 文件中的环境变量
load_dotenv()
chat_router = APIRouter()

# prompt = ChatPromptTemplate.from_template("tell me a joke about {topic}")
# add_routes(
#     chat_router,
#     prompt | model,
#     path="/joke",
# )


# 使用 itertools 的 count 函数来生成自增的 id
id_counter = count()

# 定义生成器函数以流式发送数据
async def chat_streamer(
        request: Request, 
        query: str = "what color is the sky?", 
        retrieval_documents=None, 
        model_params={"model": "gpt-3.5-turbo"}
        ):
    print("开始回答问题！！！！！！！！！")
    print(model_params)
    print("开始回答问题！！！！！！！！！")
    print(model_params)
    model = ChatOpenAI(**model_params)
    yield {"data": json.dumps(retrieval_documents, ensure_ascii=False), "event": "quotation", "id": -1}
    # 生成器函数，用于流式发送数据
    async for chunk in model.astream(query):
        print(chunk)
        if await request.is_disconnected():
            print("连接已中断")
            break
        id = next(id_counter)  # 获取下一个自增的 id
        data = json.dumps({"content": chunk.content, "id": chunk.id}, ensure_ascii=False)
        yield {"data": data, "event": "message", "id": id}

# class QueryModel(BaseModel):
#     query: str = "what color is the sky?"
#     dataset_ids: Optional[list[UUID]] = None
#     model_name: Optional[str] = Field(None, title="模型名称", description="大语言模型的名称")
#     model_temperature: Optional[float] = Field(None, title="模型温度", description="大语言模型的温度参数")
#     model_max_tokens: Optional[int] = Field(None, title="最大令牌数", description="大语言模型生成的最大令牌数")
#     model_history_window_length: Optional[int] = Field(None, title="历史窗口长度", description="大语言模型的历史窗口长度")
#     prompt_template: Optional[str] = Field(None, title="提示词模板", description="用于大语言模型的提示词模板")
#     citation_limit: Optional[int] = Field(None, title="引用限制", description="关联知识库的引用限制")
#     min_relevance: Optional[float] = Field(None, title="最小相关性", description="关联知识库的最小相关性")

class QueryModel(BaseModel):
    query: str = "what color is the sky?"
    appset_id: UUID

# @chat_router.post("/test", tags=["chat"])
# async def chat_test(query_body: QueryModel):
#     appset = await APPSet.get(id=query_body.appset_id).prefetch_related('datasets')
#     appset = await APPSet.get(id=query_body.appset_id).prefetch_related('datasets')
#     dataset_ids = [dataset.id for dataset in appset.datasets]
#     return appset

# 创建一个FastAPI路由来处理流式响应
@chat_router.post("/", tags=["chat"])
async def chat(request: Request, query_body: QueryModel):
    # 通过appset_id 查询 appset 参数 / datasets_ids 参数
    appset = await APPSet.get(id=query_body.appset_id).prefetch_related('datasets')
    dataset_ids = [dataset.id for dataset in appset.datasets]
    
    docs_and_scores = retrieval_similarity_search(
        dataset_ids, 
        query_body.query, 
        appset.citation_limit, 
        appset.min_relevance
    )

    if appset.prompt_template:
        template = appset.prompt_template
    else:
        template = "你是一个用于回答问题的助手。请使用以下检索到的上下文片段来回答问题。\n\
            如果你不知道答案，只需说你不知道。最好用markdown格式回答问题。\n\
            问题: {question}\n\
            上下文: {context}\n\
            回答:"

    # 提取并拼接每个 document.page_content
    context = "\n\n".join(doc["page_content"] for doc in docs_and_scores)
    retrieval_query = HumanMessage(content=template.format(question=query_body.query, context=context))
    print(retrieval_query.content)

    # HumanMessage 需要用 [ ] 包裹 起来
    model_params = {
        "model": appset.model_name,
        "temperature": appset.model_temperature,
        **({"max_tokens": appset.model_max_tokens} if appset.model_max_tokens is not None else {})
    }
    return EventSourceResponse(
        chat_streamer(request, 
                      query=[retrieval_query], 
                      retrieval_documents=docs_and_scores, 
                      model_params=model_params))