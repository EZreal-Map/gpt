from langchain_openai import ChatOpenAI
from fastapi import APIRouter, Request, HTTPException, Body
from itertools import count
from sse_starlette import EventSourceResponse
from pydantic import BaseModel, Field
import json
from utils.retrieval import retrieval_similarity_search
from typing import Dict, List
from langchain_core.messages import HumanMessage, AIMessage
from models.models import APPSet, ChatSet, ChatHistory, FileSet, NormalUser
from utils.templates import retrieval_template, title_template, user_analyze_template
from routers.dataset import PrivacyEnum
from tortoise.exceptions import DoesNotExist

from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 创建一个APIRouter实例
chat_router = APIRouter()


async def get_recent_chat_histories(
    appset_id: str, chat_id: str, is_test_mode: bool, n: int
) -> List[Dict[str, str]]:
    """
    查询指定 appset_id 和 chat_id 的最近 n 条 ChatHistory 记录，并提取 question 和 answer。

    :param appset_id: APPSet 的 ID
    :param chat_id: ChatSet 的 ID
    :param is_test_mode: 是否为测试模式
    :param n: 要查询的记录数量
    :return: 包含 question 和 answer 的 JSON 格式列表
    """
    # 查询指定的 APPSet
    appset = await APPSet.filter(id=appset_id).first()
    if not appset:
        raise HTTPException(status_code=404, detail="未找到指定的 APPSet")

    # 如果是测试模式，使用默认的测试 ChatSet
    if is_test_mode:
        chat_set = await ChatSet.filter(app_id=appset.id, is_test=True).first()
        if not chat_set:
            raise HTTPException(status_code=404, detail="未找到测试 ChatSet")

    else:
        # 否则，判断 chat_id 是否存在
        if chat_id:  # 如果提供了 chat_id，代表有历史对话上下文
            chat_set = await ChatSet.filter(id=chat_id, app_id=appset.id).first()
            if not chat_set:
                raise HTTPException(status_code=404, detail="未找到指定的 ChatSet")
        else:  # 如果没有提供 chat_id，代表是新建对话模式的第一句话，没有历史对话上下文
            return []

    # 查询最近 n 条 ChatHistory 记录
    recent_histories = (
        await ChatHistory.filter(chat_id=chat_set.id).order_by("-created_at").limit(n)
    )

    # 提取 question 和 answer
    qa_dict = [
        {"question": history.question, "answer": history.answer}
        for history in recent_histories
    ]

    return qa_dict


# 定义生成器函数以流式发送数据
async def chat_streamer(
    request: Request,
    query: str = "what color is the sky?",
    retrieval_documents=None,
    context_history=None,
    model_params={"model": "gpt-3.5-turbo"},
):
    print("开始回答问题！！！！！！！！！")
    print(model_params)
    # 使用 itertools 的 count 函数来生成自增的 id
    id_counter = count()
    # 模型：创建 ChatOpenAI 实例
    model = ChatOpenAI(**model_params)
    if retrieval_documents:
        yield {
            "data": json.dumps(retrieval_documents, ensure_ascii=False),
            "event": "quotation",
            "id": -1,
        }
    if context_history:
        yield {
            "data": json.dumps(context_history, ensure_ascii=False),
            "event": "context_history",
            "id": -2,
        }
    # 生成器函数，用于流式发送数据
    async for chunk in model.astream(query):
        print(chunk)
        if await request.is_disconnected():
            print("连接已中断")
            break
        id = next(id_counter)  # 获取下一个自增的 id
        data = json.dumps(
            {"content": chunk.content, "id": chunk.id}, ensure_ascii=False
        )
        yield {"data": data, "event": "message", "id": id}


class QueryModel(BaseModel):
    query: str = Field("what color is the sky?", description="查询的问题")
    appset_id: str = Field(..., description="APPSet的ID，确认模型参数与检索参数")
    chat_id: str = Field(None, description="ChatSet的ID，可选, 用来查询历史对话上下文")
    is_test_mode: bool = Field(False, description="是否为测试模式")
    fileset_id: str = Field(
        None, description="FileSet的ID，可选, 用来查询历史对话上下文"
    )


# 创建一个FastAPI路由来处理流式响应
# 用户发送问题，返回答案路由 /chat
@chat_router.post("", tags=["chat"])
async def retrieval_chat(request: Request, query_body: QueryModel):
    # 通过appset_id 查询 appset 参数 / datasets_ids 参数
    try:
        # 尝试获取 APPSet 对象并预取关联数据
        appset = await APPSet.get(id=query_body.appset_id).prefetch_related("datasets")
    except:
        # 如果对象不存在，记录日志并抛出 HTTP 404 异常
        raise HTTPException(status_code=404, detail="未找到指定的 APPSet")

    if appset.privacy == PrivacyEnum.PRIVATE.value:
        # is_login = await is_user_logged_in(request)
        # if not is_login:
        raise HTTPException(status_code=403, detail=f"禁止访问send_message")
    # 获取 appset 中所有公开 知识库的 id
    dataset_ids = [
        dataset.id
        for dataset in appset.datasets
        if dataset.privacy == PrivacyEnum.PUBLIC.value
    ]
    # 查询fileset_id 有没有fileset，如果有代表有files需要检索
    try:
        fileset = await FileSet.get(
            id=query_body.fileset_id
        )  # 通过 fileset_id 查询数据库
        dataset_ids.append(fileset.id)  # 将 fileset_id 添加到 dataset_ids 中
    except DoesNotExist:
        print("fileset_id 不存在，不需要检索文件")

    # 使用 retrieval_similarity_search 函数检索相关文档 检索能力
    docs_and_scores = retrieval_similarity_search(
        dataset_ids, query_body.query, appset.citation_limit, appset.min_relevance
    )

    if appset.prompt_template:
        template = appset.prompt_template
    else:
        template = retrieval_template

    # 提取并拼接每个 document.page_content
    context = "\n\n".join(doc["page_content"] for doc in docs_and_scores)
    retrieval_context = HumanMessage(
        content=template.format(question=query_body.query, context=context)
    )
    print(retrieval_context.content)
    # 获取最近的 n 条对话历史记录 上下文能力
    # 使用 await 等待异步函数的执行完成
    qa_dict = await get_recent_chat_histories(
        appset_id=query_body.appset_id,
        chat_id=query_body.chat_id,
        is_test_mode=query_body.is_test_mode,
        n=appset.model_history_window_length,
    )
    print("qa_dict:", qa_dict)
    # 生成一个包含 HumanMessage 和 AIMessage 对象的列表
    query = []
    for qa in qa_dict:
        query.append(HumanMessage(content=qa["question"]))
        query.append(AIMessage(content=qa["answer"]))
    print("history_context:", query)
    query.append(retrieval_context)

    # 一定保证 prompt + max_tokens <= model_context (提问 + max_tokens <= 模型上下文)
    model_params = {
        "model": appset.model_name,
        "temperature": appset.model_temperature,
        "max_tokens": appset.model_max_tokens,
    }

    # 如果query只有一个 HumanMessage 需要用 [ ] 包裹 起来
    return EventSourceResponse(
        chat_streamer(
            request,
            query=query,
            retrieval_documents=docs_and_scores,
            context_history=qa_dict,
            model_params=model_params,
        )
    )


class QAModel(BaseModel):
    chat_id: str = Field(None, description="ChatSet的ID，可选, 用来更新chatset name")
    question: str = Field("what color is the sky?", description="问题")
    answer: str = Field("blue", description="回答")


# 创建一个FastAPI路由来处理流式响应, 传入新建的第一个QA对话，取一个标题名字
@chat_router.post("/title", tags=["chat"])
async def retrieval_chat(qa_body: QAModel):

    template = title_template
    query = template.format(question=qa_body.question, answer=qa_body.answer)

    model = ChatOpenAI()

    title_name = model.invoke(query).content
    # 查询指定的 ChatSet
    chatset = await ChatSet.get_or_none(id=qa_body.chat_id)
    if not chatset:
        raise HTTPException(status_code=404, detail="未找到指定的 ChatSet")
    chatset.name = title_name
    await chatset.save()
    return {"title_name": title_name, "chatset": chatset}


# 提供给UE的接口，传入query，返回修饰后的query
# 创建一个FastAPI路由，获取 query 修饰后的 query string 添加 RAG 和 历史上下文
@chat_router.post("/ue", tags=["chat"])
async def retrieval_chat(request: Request, query_body: QueryModel):
    print("query_body:", query_body)
    # 通过appset_id 查询 appset 参数 / datasets_ids 参数
    try:
        # 尝试获取 APPSet 对象并预取关联数据
        appset = await APPSet.get(id=query_body.appset_id).prefetch_related("datasets")
    except:
        # 如果对象不存在，记录日志并抛出 HTTP 404 异常
        raise HTTPException(status_code=404, detail="未找到指定的 APPSet")

    if appset.privacy == PrivacyEnum.PRIVATE.value:
        # is_login = await is_user_logged_in(request)
        # if not is_login:
        raise HTTPException(status_code=403, detail=f"禁止访问send_message")
    # 获取 appset 中所有公开 知识库的 id
    dataset_ids = [
        dataset.id
        for dataset in appset.datasets
        if dataset.privacy == PrivacyEnum.PUBLIC.value
    ]
    # 使用 retrieval_similarity_search 函数检索相关文档 检索能力
    docs_and_scores = retrieval_similarity_search(
        dataset_ids, query_body.query, appset.citation_limit, appset.min_relevance
    )

    if appset.prompt_template:
        template = appset.prompt_template
    else:
        template = retrieval_template

    # 提取并拼接每个 document.page_content
    context = "\n\n".join(doc["page_content"] for doc in docs_and_scores)
    retrieval_context = HumanMessage(
        content=template.format(question=query_body.query, context=context)
    )
    print(retrieval_context.content)
    # 获取最近的 n 条对话历史记录 上下文能力
    # 使用 await 等待异步函数的执行完成
    qa_dict = await get_recent_chat_histories(
        appset_id=query_body.appset_id,
        chat_id=query_body.chat_id,
        is_test_mode=query_body.is_test_mode,
        n=appset.model_history_window_length,
    )
    print("qa_dict:", qa_dict)
    # 生成一个包含 HumanMessage 和 AIMessage 对象的列表
    query = []
    for qa in qa_dict:
        query.append(HumanMessage(content=qa["question"]))
        query.append(AIMessage(content=qa["answer"]))
    print("history_context:", query)
    query.append(retrieval_context)

    # 上面是一样的，和retrieval_chat一样
    # 构造查询字符串
    query_string = ""
    for q in query:
        if isinstance(q, HumanMessage):
            query_string += f"HumanMessage:{q.content}\n"
        elif isinstance(q, AIMessage):
            query_string += f"AIMessage:{q.content}\n"

    print("query_string:", query_string)

    return {"query:": query_string}


class UserAnalyzeModel(BaseModel):
    student_id: str = Field(..., description="学号")


# 处理用户分析路由
@chat_router.post("/user_analyze", tags=["chat"])
async def user_analyze_chat(request: Request, user: UserAnalyzeModel):
    # 先通过user_id 查询 NormalUser的id
    normal_user = await NormalUser.get_or_none(user_id=user.student_id)
    # 通过user_id 查询 chatset 再查询 chat_history
    # 获取所有与用户相关的 ChatSet 的 ID 列表
    chatset_ids = await ChatSet.filter(user_id=normal_user.id).values_list(
        "id", flat=True
    )

    # 使用 in 查询所有对应的 ChatHistory 记录数
    questions = (
        await ChatHistory.filter(chat_id_id__in=chatset_ids)
        .order_by("-updated_at")
        .limit(50)
        .values_list("question", flat=True)
    )

    template = user_analyze_template
    query = HumanMessage(
        content=template.format(
            student_name=normal_user.name,
            student_id=user.student_id,
            questions=questions,
        )
    )
    return EventSourceResponse(chat_analyze(request, query=query))


async def chat_analyze(
    request: Request, query: HumanMessage, model_params={"model": "gpt-4o"}
):
    # 使用 itertools 的 count 函数来生成自增的 id
    id_counter = count()
    # 模型：创建 ChatOpenAI 实例
    model = ChatOpenAI(**model_params)
    # 生成器函数，用于流式发送数据
    async for chunk in model.astream(query.content):
        # print(chunk)
        if await request.is_disconnected():
            print("连接已中断")
            break
        id = next(id_counter)  # 获取下一个自增的 id
        data = json.dumps(
            {"content": chunk.content, "id": chunk.id}, ensure_ascii=False
        )
        yield {"data": data, "event": "message", "id": id}
