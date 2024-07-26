from fastapi import APIRouter, HTTPException
from models.models import APPSet

# 创建一个APIRouter实例
appset_router_no_auth = APIRouter()

# 获取指定{appset_id} APPSet 的路由
@appset_router_no_auth.get("/{appset_id}", tags=["appset"])
async def get_dataset(appset_id: str):
    """
    获取一个指定的APPSet
    :param appset_id: 数据集ID
    :return: 查询后的数据库记录
    """
    appset = await APPSet.get_or_none(id=appset_id)
    if not appset:
        raise HTTPException(status_code=404, detail="Appset not found")
    appset.created_at = appset.created_at.strftime('%Y-%m-%d %H:%M:%S')
    return appset