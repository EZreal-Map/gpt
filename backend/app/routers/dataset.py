from fileinput import filename
from fastapi import APIRouter, HTTPException, Body
from models.models import DataSet
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from enum import Enum
import os
import shutil
from pathlib import Path
from utils.retrieval import PDF_to_documents, load_vectorstore, transform_data
from models.models import Article

# 创建一个APIRouter实例
dataset_router = APIRouter()

# 定义枚举类
class PrivacyEnum(str, Enum):
    PRIVATE = "私有"
    PUBLIC = "公开"

# 定义 Pydantic 模型用于请求体验证
class DataSetCreate(BaseModel):
    name: str
    description: Optional[str] = None
    privacy: PrivacyEnum

class DataSetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    privacy: Optional[PrivacyEnum] = None

# 定义 Pydantic 模型用于响应体验证
class DataSetResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    privacy: str

# 获取所有 DataSet 的路由
@dataset_router.get("/", response_model=List[DataSetResponse])
async def get_all_datasets():
    """
    获取所有数据集
    :return: 数据集列表
    """
    return await DataSet.all()

# 创建新的 DataSet 的路由
@dataset_router.post("/", response_model=DataSetResponse)
async def create_dataset(dataset: DataSetCreate):
    """
    创建一个新的数据集
    :param dataset: 数据集信息
    :return: 创建的数据库记录
    """
    # 创建新的数据集记录
    new_dataset = await DataSet.create(**dataset.dict())

    # 创建新的文件夹
    folder_path = f"static/document/{new_dataset.id}"
    os.makedirs(folder_path, exist_ok=True)

    return new_dataset

# 删除指定 DataSet 的路由
@dataset_router.delete("/{dataset_id}", response_model=dict)
async def delete_dataset(dataset_id: UUID):
    """
    删除一个数据集
    :param dataset_id: 数据集ID
    :return: 删除结果消息
    """
    dataset = await DataSet.get_or_none(id=dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # 查询关联的 Article 记录并删除
    articles = await Article.filter(dataset_id=dataset_id).all()
    for article in articles:
        await article.delete()
    
    # 删除数据库记录
    await dataset.delete()
    
    # 删除对应的文件夹
    folder_path = f"static/document/{dataset_id}"
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    
    return {"message": "Dataset deleted successfully"}

# 更新指定 DataSet 的路由
@dataset_router.put("/{dataset_id}", response_model=DataSetResponse)
async def update_dataset(dataset_id: UUID, dataset_update: DataSetUpdate):
    """
    更新一个数据集
    :param dataset_id: 数据集ID
    :param dataset_update: 更新的信息
    :return: 更新后的数据库记录
    """
    dataset = await DataSet.get_or_none(id=dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    update_data = dataset_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(dataset, key, value)
    await dataset.save()
    return dataset


def extract_unique_info(documents):
    filename_info = {}
    for document in documents:
        filename = document.metadata["filename"]
        total_word_count = document.metadata["total_word_count"]
        chunk_sum_num = document.metadata["chunk_sum_num"]
        
        if filename not in filename_info:
            filename_info[filename] = {
                "total_word_count": total_word_count,
                "chunk_sum_num": chunk_sum_num
            }
    return filename_info

# 将 temp_dir 中的所有文件移动到指定的 dataset 目录下的路由
@dataset_router.post("/move-temp-files/{dataset_id}", response_model=dict)
async def move_temp_files_to_dataset(dataset_id: UUID,
                                    chunk_size: int = Body(default=500, ge=0), 
                                    chunk_overlap: int = Body(default=100, ge=0), 
                                    separator: str = Body(default="")):
    """
    将 temp_dir 中的所有文件移动到指定的 dataset 目录下
    :param dataset_id: 数据集ID
    :return: 移动结果消息
    """
    dataset = await DataSet.get_or_none(id=dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    temp_dir = Path("static/temp")
    target_dir = Path(f"static/document/{dataset_id}")

    if not temp_dir.exists():
        raise HTTPException(status_code=404, detail="Temp directory not found")
    
    if not target_dir.exists():
        raise HTTPException(status_code=404, detail="Temp directory not found")

    filenames = []

    for item in temp_dir.iterdir():
        target_file_path = target_dir / item.name
        shutil.move(str(item), target_file_path)
        filenames.append(str(target_file_path))

    # 将 PDF 文件转换为文档内容
    documents = PDF_to_documents(filenames, chunk_size, chunk_overlap, separator)

    filename_info = extract_unique_info(documents)
    for filename, info in filename_info.items():
        # 创建 Article 实例并保存到数据库
        await Article.create(
            dataset_id=dataset,
            name=filename,
            character_count=info["total_word_count"],  # 总字数
            chunk_sum_num=info["chunk_sum_num"]  # 总分块数   
        )

    vectorstore = load_vectorstore(dataset_id)
    vectorstore.add_documents(documents)

    return {
            "message": "Files moved successfully", 
            "filename_info": filename_info, 
            "documents": documents, 
            "vectorstore":vectorstore.get()
            }


# 获取特定数据集（dataset_id）对应的所有文章数据的路由
@dataset_router.get("/{dataset_id}/articles")
async def get_articles_by_dataset_id(dataset_id: UUID):
    """
    获取特定数据集（dataset_id）对应的所有文章数据
    :param dataset_id: 数据集ID
    :return: 文章数据列表
    """
    articles = await Article.filter(dataset_id=dataset_id).all()
    return articles


# 获取特定文章（article_id）对应的所有分块数据的路由
@dataset_router.get("/{article_id}/chunks")
async def get_chunks_by_article_id(article_id: UUID):
    """
    获取特定文章（article_id）对应的所有分块数据
    :param article_id: 文章ID
    :return: 分块数据列表
    """
    article = await Article.get_or_none(id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # 获取文章对应的数据集ID的实体，一定要加 await，要不然查询不到
    dataset = await article.dataset_id 
    
    # 加载向量数据库
    vectorstore = load_vectorstore(dataset.id)

    # 使用 `where` 参数进行过滤  metadata.filename == article.name
    filename_chunks = vectorstore.get(where={"filename": article.name})
    transform_filename_chunks = transform_data(filename_chunks,keys=["ids", "metadatas", "documents"])
    transform_filename_chunks = sorted(transform_filename_chunks, key=lambda x: x['metadatas']['chunk_count'])
    
    return transform_filename_chunks