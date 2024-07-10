
from fastapi import APIRouter, HTTPException
from models.models import APPSet, DataSet
from enum import Enum
from pydantic import BaseModel
from typing import List, Optional, Union
from uuid import UUID
from datetime import datetime

# 创建一个APIRouter实例
appset_router = APIRouter()

# 定义枚举类
class PrivacyEnum(str, Enum):
    PRIVATE = "私有"
    PUBLIC = "公开"

# 定义 Pydantic 模型用于请求体验证
class APPSetPydantic(BaseModel):
    name: str
    description: Optional[str] = None
    privacy: PrivacyEnum

# 定义 Pydantic 模型用于响应体验证
class APPSetResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    privacy: str
    created_at: Union[str, datetime]

# 获取所有 APPSet 的路由
@appset_router.get("/", response_model=List[APPSetResponse], tags=["appset"])
async def get_all_datasets():
    """
    获取所有APP应用数据集
    :return: APP应用数据集列表
    """
    appsets = await APPSet.all().order_by('-created_at')
    for appset in appsets:
        appset.created_at = appset.created_at.strftime('%Y-%m-%d %H:%M:%S')
    return appsets


# 创建新的 APPSet 的路由
@appset_router.post("/", response_model=APPSetResponse, tags=["appset"])
async def create_dataset(appset: APPSetPydantic):
    """
    创建一个新的APP应用数据集
    :param appset: APP应用数据集信息
    :return: 创建的APP应用数据记录
    """
    # 创建新的数据集记录
    new_appset = await APPSet.create(**appset.dict())

    # 创建新的文件夹
    # folder_path = f"static/document/{new_appset.id}"
    # os.makedirs(folder_path, exist_ok=True)

    return new_appset

# 更新指定 APPSet 的路由
@appset_router.put("/{appset_id}", response_model=APPSetResponse, tags=["appset"])
async def update_dataset(appset_id: str, appset_update: APPSetPydantic):
    """
    更新一个数据集
    :param appset_id: 数据集ID
    :param appset_update: 更新的信息
    :return: 更新后的数据库记录
    """
    appset = await APPSet.get_or_none(id=appset_id)
    if not appset:
        raise HTTPException(status_code=404, detail="Appset not found")
    update_data = appset_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(appset, key, value)
    await appset.save()
    return appset

# 删除指定 APPSet 的路由
@appset_router.delete("/{appset_id}", response_model=dict, tags=["appset"])
async def delete_dataset(appset_id: UUID):
    """
    删除一个数据集
    :param appset_id: 数据集ID
    :return: 删除结果消息
    """
    appset = await APPSet.get_or_none(id=appset_id)
    if not appset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # 删除数据库记录
    await appset.delete()
    return {
        "appset": appset
        }

# 获取指定{appset_id} APPSet 的路由
@appset_router.get("/{appset_id}", response_model=APPSetResponse, tags=["appset"])
async def update_dataset(appset_id: str):
    """
    更新一个数据集
    :param appset_id: 数据集ID
    :return: 查询后的数据库记录
    """
    appset = await APPSet.get_or_none(id=appset_id)
    if not appset:
        raise HTTPException(status_code=404, detail="Appset not found")
    appset.created_at = appset.created_at.strftime('%Y-%m-%d %H:%M:%S')
    return appset


# 更新或添加 APPSet 的 datasets 集合
@appset_router.put("/{appset_id}/datasets", tags=["appset"])
async def update_appset_datasets(appset_id: str, dataset_ids: List[UUID]):
    """
    更新或添加 APPSet 的 datasets 集合
    :param appset_id: 数据集ID
    :param dataset_ids: 要更新或添加的 dataset IDs
    :return: 更新后的数据库记录
    """
    appset = await APPSet.get_or_none(id=appset_id)
    if not appset:
        raise HTTPException(status_code=404, detail="Appset not found")

    # 清空原有的关联
    await appset.datasets.clear()

    # 添加新的关联 DataSet
    for dataset_id in dataset_ids:
        dataset = await DataSet.get_or_none(id=dataset_id)
        if dataset:
            await appset.datasets.add(dataset)

    await appset.save()

    # 返回更新后的 APPSet 数据
    # appset = await APPSet.get_or_none(id=appset_id)
    # 返回更新后的 datasets IDs 列表
    updated_dataset_ids = [dataset.id for dataset in await appset.datasets.all()]
    return updated_dataset_ids


# 获取指定 APPSet 关联的所有 DataSet 数据
@appset_router.get("/{appset_id}/datasets", tags=["appset"])
async def get_appset_datasets(appset_id: str):
    """
    获取指定 APPSet 关联的所有 DataSet 数据
    :param appset_id: 数据集ID
    :return: 关联的所有 DataSet 数据列表
    """
    appset = await APPSet.get_or_none(id=appset_id)
    if not appset:
        raise HTTPException(status_code=404, detail="Appset not found")

    # 查询关联的所有 DataSet 数据
    datasets = await appset.datasets.all()
    for dataset in datasets:
        dataset.created_at = dataset.created_at.strftime('%Y-%m-%d %H:%M:%S')
    return datasets