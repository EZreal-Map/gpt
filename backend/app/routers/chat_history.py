from fastapi import APIRouter, HTTPException, Path

from models.models import ChatHistory

# 创建一个APIRouter实例
chat_history_router = APIRouter()


# 删除一个 ChatHistory
@chat_history_router.delete("/{chat_history_id}", tags=["chat history"])
async def delete_chat_history(
    chat_history_id: str = Path(..., description="ChatHistory 的 ID")
):
    # 查询指定的 ChatHistory
    chat_history = await ChatHistory.get_or_none(id=chat_history_id)
    if not chat_history:
        raise HTTPException(status_code=404, detail="未找到指定的 ChatHistory")

    # 删除 ChatHistory
    await chat_history.delete()
    return {"detail": "ChatHistory 删除成功"}
