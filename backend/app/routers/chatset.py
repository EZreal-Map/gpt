from fastapi import APIRouter, HTTPException, Path, Query, Body
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from models.models import APPSet, ChatSet, ChatHistory, Article


# 创建一个APIRouter实例
chatset_router = APIRouter()


class CiteDocument(BaseModel):
    metadata: Dict[str, Any] = Field(..., description="元数据")
    page_content: str = Field(..., description="页面内容")
    score: float = Field(..., description="分数")
    type: str = Field(..., description="类型")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metadata": self.metadata,
            "page_content": self.page_content,
            "score": self.score,
            "type": self.type,
        }


class ChatHistoryCreate(BaseModel):
    # 创建新对话历史记录的模式
    appset_id: str = Field(..., description="APPSet的ID")
    chat_id: Optional[str] = Field(
        None, description="ChatSet的ID"
    )  # 如果没有提供 chat_id，存储到默认的测试 ChatSet
    question: str = Field(..., description="提出的问题")
    answer: str = Field(..., description="对问题的回答")
    cite_documents: Optional[List[CiteDocument]] = Field(
        [], description="检索到的引用记录"
    )
    context_histories: Optional[list[Dict[str, Any]]] = Field(
        [], description="历史上下文记录"
    )
    execute_time: float = Field(..., description="对话操作的执行时间")
    is_test_mode: bool = Field(False, description="是否为测试模式")


# 与 ChatSet 有关 ChatHistory 的 CRUD 路由
# 添加指定chat_id/默认id的一条对话历史记录路由
@chatset_router.post("/{appset_id}/chat_history", tags=["chat_history"])
async def add_test_chat_history(chat_history: ChatHistoryCreate):
    # 查询指定的 APPSet
    appset = await APPSet.filter(id=chat_history.appset_id).first()
    if not appset:
        raise HTTPException(status_code=404, detail="未找到指定的 APPSet")

    # 如果提供了 chat_id，使用对应的 ChatSet
    if chat_history.chat_id:
        chat_set = await ChatSet.filter(id=chat_history.chat_id).first()
        chat_set_mode = "old_chat_set"
        if not chat_set:
            raise HTTPException(status_code=404, detail="未找到指定的 ChatSet")
    else:
        if chat_history.is_test_mode:
            # 使用默认的测试 ChatSet
            chat_set = await ChatSet.filter(app_id=appset, is_test=True).first()
            chat_set_mode = "test_chat_set"
            if not chat_set:
                raise HTTPException(status_code=404, detail="未找到测试 ChatSet")
        else:
            # 创建新的 ChatSet, is_test 设置为 False
            chat_set = await ChatSet.create(app_id=appset, is_test=False)
            chat_set_mode = "new_chat_set"

    # 引用记录(集合) 的序列化
    cite_documents = [doc.to_dict() for doc in chat_history.cite_documents]
    # 创建对话历史记录
    new_chat_history = await ChatHistory.create(
        chat_id=chat_set,
        question=chat_history.question,
        answer=chat_history.answer,
        # 直接将 CiteDocument 对象存入数据库，会导致类型不可序列化的错误
        # Convert each CiteDocument to dict before storing in the database
        cite_documents=cite_documents,
        context_histories=chat_history.context_histories,
        execute_time=chat_history.execute_time,
    )

    # 更新引用记录的 recall_count
    for cite_document in cite_documents:
        article = await Article.get_or_none(id=cite_document["metadata"]["article_id"])
        if not article:
            raise HTTPException(status_code=404, detail="未找到指定的 Article")
        article.recall_count += 1
        await article.save()

    return {
        "chat_set_mode": chat_set_mode,
        "chat_set_id": chat_set.id,
        "chat_history_id": new_chat_history.id,
    }


# 获取指定chat_id/默认id的全部对话历史路由
@chatset_router.get("/{appset_id}/chat_history", tags=["chat_history"])
async def get_test_chat_set(
    appset_id: str = Path(..., description="APPSet 的 ID"),
    chat_id: str = Query(None, description="ChatSet 的 ID，可选"),
):
    # 查询指定的 APPSet
    appset = await APPSet.filter(id=appset_id).first()
    if not appset:
        raise HTTPException(status_code=404, detail="未找到指定的 APPSet")

    # 如果提供了 chatset_id，使用对应的 ChatSet
    if chat_id:
        chat_set = await ChatSet.filter(id=chat_id, app_id=appset).first()
        if not chat_set:
            raise HTTPException(status_code=404, detail="未找到指定的 ChatSet")
    else:
        # 否则，使用默认的测试 ChatSet
        chat_set = await ChatSet.filter(app_id=appset, is_test=True).first()
        if not chat_set:
            raise HTTPException(status_code=404, detail="未找到测试 ChatSet")

    # 获取该 ChatSet 的所有对话历史记录
    chat_histories = await ChatHistory.filter(chat_id=chat_set).all()

    # 整理返回的数据
    result = []
    for history in chat_histories:
        result.append(
            {
                "id": history.id,
                "question": history.question,
                "answer": history.answer,
                "cite_documents": history.cite_documents,
                "context_histories": history.context_histories,
                "execute_time": history.execute_time,
                "created_at": history.created_at,
            }
        )

    return result


# 清空指定chat_id/默认id的全部对话历史路由
@chatset_router.delete("/{appset_id}/chat_history", tags=["chat_history"])
async def delete_chat_set_history(
    appset_id: str = Path(..., description="APPSet 的 ID"),
    chat_id: str = Query(None, description="ChatSet 的 ID，可选"),
):
    # 查询指定的 APPSet
    appset = await APPSet.filter(id=appset_id).first()
    if not appset:
        raise HTTPException(status_code=404, detail="未找到指定的 APPSet")

    if chat_id:
        # 删除指定的 ChatSet 及其历史记录
        chat_set = await ChatSet.filter(id=chat_id, app_id=appset).first()
        if not chat_set:
            raise HTTPException(status_code=404, detail="未找到指定的 ChatSet")
        await chat_set.delete()
    else:
        # 否则，使用默认的测试 ChatSet
        chat_set = await ChatSet.filter(app_id=appset, is_test=True).first()
        if not chat_set:
            raise HTTPException(status_code=404, detail="未找到测试 ChatSet")
            # 获取该 ChatSet 的所有对话历史记录
        chat_histories = await ChatHistory.filter(chat_id=chat_set).all()
        for chat_history in chat_histories:
            await chat_history.delete()
    return {"detail": "聊天记录清除成功"}


# 有关 ChatSet 的 CRUD 路由
# 根据 appset_id 返回所有与 appset_id 关联的 chatset (is_test=True除外)
@chatset_router.get("/{appset_id}/chatset", tags=["chatset"])
async def get_related_chat_ids(appset_id: str = Path(..., description="APPSet 的 ID")):
    # 查询指定的 APPSet
    appset = await APPSet.get_or_none(id=appset_id)
    if not appset:
        raise HTTPException(status_code=404, detail="未找到指定的 APPSet")

    # 查询与该 APPSet 关联的所有 ChatSet 的 ID
    chatsets = (
        await ChatSet.filter(app_id=appset, is_test=False).all().order_by("-created_at")
    )
    for chatset in chatsets:
        chatset.created_at = chatset.created_at.strftime("%Y-%m-%d %H:%M:%S")
    return chatsets


# 更新一个 ChatSet 的名称
@chatset_router.put("/{chat_id}", tags=["chatset"])
async def update_chatset_name(
    chat_id: str = Path(..., description="ChatSet 的 ID"),
    chat_name: str = Body(..., description="ChatSet 的名称"),
):
    # 查询指定的 ChatSet
    chatset = await ChatSet.get_or_none(id=chat_id)
    if not chatset:
        raise HTTPException(status_code=404, detail="未找到指定的 ChatSet")

    # 更新 ChatSet 的名称
    chatset.name = chat_name
    await chatset.save()
    return {"detail": "ChatSet 名称更新成功"}


# 删除一个 ChatSet
@chatset_router.delete("/{chat_id}", tags=["chatset"])
async def delete_chatset(chat_id: str = Path(..., description="ChatSet 的 ID")):
    # 查询指定的 ChatSet
    chatset = await ChatSet.get_or_none(id=chat_id)
    if not chatset:
        raise HTTPException(status_code=404, detail="未找到指定的 ChatSet")

    # 删除 ChatSet
    await chatset.delete()
    return {"detail": "ChatSet 删除成功"}
