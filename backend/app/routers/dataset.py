from fastapi import APIRouter, HTTPException, Body, Query
from models.models import DataSet, Article, QueryTestHistory
from pydantic import BaseModel, validator
from typing import List, Optional, Union
from uuid import UUID
from enum import Enum
import os
import shutil
from pathlib import Path
from utils.retrieval import PDF_to_documents, load_vectorstore, transform_data
from fastapi.responses import FileResponse
from langchain.docstore.document import Document
from datetime import datetime

# 创建一个APIRouter实例
dataset_router = APIRouter()


# 定义枚举类
class PrivacyEnum(str, Enum):
    PRIVATE = "私有"
    PUBLIC = "公开"


# 定义 Pydantic 模型用于请求体验证
class DataSetPydantic(BaseModel):
    name: str
    description: Optional[str] = None
    privacy: PrivacyEnum


# 定义 Pydantic 模型用于响应体验证
class DataSetResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    privacy: str
    created_at: Union[str, datetime]


# 获取所有 DataSet 的路由
@dataset_router.get("/", response_model=List[DataSetResponse], tags=["dataset"])
async def get_all_datasets():
    """
    获取所有数据集
    :return: 数据集列表
    """
    datasets = await DataSet.all().order_by("-created_at")
    for dataset in datasets:
        dataset.created_at = dataset.created_at.strftime("%Y-%m-%d %H:%M:%S")
    return datasets


# 创建新的 DataSet 的路由
@dataset_router.post("/", response_model=DataSetResponse, tags=["dataset"])
async def create_dataset(dataset: DataSetPydantic):
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
@dataset_router.delete("/{dataset_id}", response_model=dict, tags=["dataset"])
async def delete_dataset(dataset_id: UUID):
    """
    删除一个数据集
    :param dataset_id: 数据集ID
    :return: 删除结果消息
    """
    dataset = await DataSet.get_or_none(id=dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # 查询关联的 Article 记录并删除 已经设置 on_delete=fields.CASCADE
    # articles = await Article.filter(dataset_id=dataset_id).all()
    # for article in articles:
    #     await article.delete()

    # 删除关联的 APPSet 中的关联记录  ManyToManyField 不支持 on_delete 参数
    await dataset.appsets.clear()

    # 删除数据库记录
    await dataset.delete()

    # 删除对应的文件夹
    folder_path_document = f"static/document/{dataset_id}"
    if os.path.exists(folder_path_document):
        shutil.rmtree(folder_path_document)

    # 删除对应的文件夹
    # folder_path_vectorstore = f"static/vectorstore/{dataset_id}"
    # if os.path.exists(folder_path_vectorstore):
    #     shutil.rmtree(folder_path_vectorstore)
    # 新版本删除向量数据库  client.delete_collection()
    load_vectorstore(dataset_id).delete_collection()

    return {
        "message": f"Dataset {dataset_id} has been deleted. \
            All related [articles(on_delete=fields.CASCADE), queryhistory(on_delete=fields.CASCADE), \
            appsets(join), files(local), vectorstore(client)] have been deleted.",
        "dataset": dataset,
        "folder_path_document": folder_path_document,
    }


# 更新指定 DataSet 的路由
@dataset_router.put("/{dataset_id}", response_model=DataSetResponse, tags=["dataset"])
async def update_dataset(dataset_id: UUID, dataset_update: DataSetPydantic):
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
        article_id = document.metadata["article_id"]

        if filename not in filename_info:
            filename_info[filename] = {
                "total_word_count": total_word_count,
                "chunk_sum_num": chunk_sum_num,
                "article_id": article_id,
            }
    return filename_info


# 将 temp_dir 中的所有文件移动到指定的 dataset 目录下的路由
@dataset_router.post(
    "/move-temp-files/{dataset_id}", response_model=dict, tags=["dataset"]
)
async def move_temp_files_to_dataset(
    dataset_id: UUID,
    chunk_size: int = Body(default=500, ge=0),
    chunk_overlap: int = Body(default=100, ge=0),
    separator: str = Body(default=""),
):
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
    documents = PDF_to_documents(
        filenames, chunk_size, chunk_overlap, separator, dataset_id
    )

    filename_info = extract_unique_info(documents)
    for filename, info in filename_info.items():
        # 创建 Article 实例并保存到数据库
        print("info", info)
        await Article.create(
            id=info["article_id"],
            dataset_id=dataset,
            name=filename,
            character_count=info["total_word_count"],  # 总字数
            chunk_sum_num=info["chunk_sum_num"],  # 总分块数
        )

    vectorstore = load_vectorstore(dataset_id)
    vectorstore.add_documents(documents)  # 向向量数据库中添加文档数据

    return {
        "message": "Files moved successfully",
        "filename_info": filename_info,
        "documents": documents,
        "vectorstore": vectorstore.get(),
    }


# 获取特定数据集（dataset_id）对应的所有文章数据的路由
@dataset_router.get("/{dataset_id}/articles", tags=["dataset"])
async def get_articles_by_dataset_id(dataset_id: UUID):
    """
    获取特定数据集（dataset_id）对应的所有文章数据
    :param dataset_id: 数据集ID
    :return: 文章数据列表
    """
    articles = await Article.filter(dataset_id=dataset_id).all()
    for article in articles:
        article.created_at = article.created_at.strftime("%Y-%m-%d %H:%M:%S")
        article.updated_at = article.updated_at.strftime("%Y-%m-%d %H:%M:%S")
    return articles


# 获取特定文章（article_id）对应的所有分块数据的路由
@dataset_router.get("/{article_id}/chunks", tags=["dataset"])
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
    transform_filename_chunks = transform_data(
        filename_chunks,
        keep_keys=["ids", "metadatas", "documents"],
        new_keys=["id", "metadata", "page_content"],
    )
    transform_filename_chunks = sorted(
        transform_filename_chunks, key=lambda x: x["metadata"]["chunk_count"]
    )

    return transform_filename_chunks


# 删除特定文章（article_id）和与之相关的chunks数据/document数据的路由
@dataset_router.delete("/{article_id}/delete-documents", tags=["dataset"])
async def delete_documents_by_article_id(article_id: UUID):
    """
    删除特定文章（article_id）对应的所有文档数据
    :param article_id: 文章ID
    :return: 操作结果消息
    """
    article = await Article.get_or_none(id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # 获取文章对应的数据集ID的实体，一定要加 await，要不然查询不到
    dataset = await article.dataset_id

    dataset_id = (
        dataset.id
    )  # ForeignKeyField creates an attribute with _id suffix for the actual field value
    name = article.name

    document_path = Path(f"static/document/{dataset_id}/{name}")

    # 删除文件用 os.remove 删除目录用 shutil.rmtree
    if os.path.exists(document_path):
        os.remove(document_path)

    # 加载向量数据库
    vectorstore = load_vectorstore(dataset.id)

    # 使用 `where` 参数进行过滤 metadata.filename == article.name
    filename_chunks = vectorstore.get(where={"filename": article.name})

    # 删除文档数据
    for chunk_id in filename_chunks["ids"]:
        # 假设 vectorstore.delete() 可以删除特定文档数据
        vectorstore.delete(chunk_id)  # 假设这里的删除操作可以根据文档的唯一标识符执行

    # 最后 在数据库中删除文章记录
    await article.delete()  # 使用 ORM 时可以直接调用 delete 方法删除记录

    return {
        "message": f"All documents related to article {article_id} have been deleted.",
        "chunk_deleted": filename_chunks,
    }


# 下载指定文章（article_id）对应的文件的路由
@dataset_router.get(
    "/download-file/{article_id}", response_class=FileResponse, tags=["dataset"]
)
async def download_file(article_id: UUID):
    """
    根据 article_id 下载文件
    :param article_id: 文档ID
    :return: 文件响应
    """
    article = await Article.get_or_none(id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Document not found")

    # 获取文章对应的数据集ID的实体，一定要加 await，要不然查询不到
    dataset = await article.dataset_id

    dataset_id = (
        dataset.id
    )  # ForeignKeyField creates an attribute with _id suffix for the actual field value
    name = article.name
    file_path = Path(f"static/document/{dataset_id}/{name}")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    response = FileResponse(file_path, filename=name)
    # 设置需要暴露的响应头
    response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
    return response


# # 删除指定chunk块，通过 chunk_id
# @dataset_router.delete("/{dataset_id}/delete-chunk", tags=["dataset"])
# async def delete_chunk_by_id(dataset_id: UUID,
#                              article_id: UUID = Query(None, description="Article ID for updating chunk_sum_num"),
#                              metadata_id: UUID = Query(..., description="Chunk metadata_id to delete")
#                              ):
#     """
#     删除特定数据集（dataset_id）中的一个分块数据（chunk）
#     同时更新相关的文章（article）的 chunk_sum_num 属性
#     :param dataset_id: 数据集ID
#     :param metadata_id: 分块数据ID
#     :param article_id: 文章ID，用于更新 chunk_sum_num
#     :return: 操作结果消息
#     """
#     # 加载向量数据库
#     vectorstore = load_vectorstore(dataset_id)

#     # 将 UUID 对象转换为字符串类型的 ID
#     str_metadata_id = str(metadata_id)
#    # 查询并获取指定 chunk
#     chunk = vectorstore.get(where={"document_metadata_id": str_metadata_id})

#     if not chunk["ids"]:
#         raise HTTPException(status_code=404, detail=f"Chunk with ID {metadata_id} not found in dataset {dataset_id}")

#     # 删除指定的 chunk
#     vectorstore.delete(ids=chunk["ids"])

#     # 更新文章的 chunk_sum_num
#     if article_id:
#         article = await Article.get_or_none(id=article_id)
#         if article:
#             article.chunk_sum_num -= 1
#             await article.save()

#     return {
#         "message": f"Chunk {chunk["ids"]} has been deleted from dataset {dataset_id}",
#         "chunk_deleted": chunk,
#         "article.chunk_sum_num": article.chunk_sum_num
#     }


# class EditChunkDocument(BaseModel):
#     page_content: str

# @dataset_router.put("/{dataset_id}/edit-chunk", tags=["dataset"])
# async def edit_chunk_by_id(dataset_id: UUID,
#                            edit_chunk: EditChunkDocument,
#                            chunk_id: UUID = Query(..., description="Chunk ID to edit")
#                            ):
#     """
#     编辑特定数据集（dataset_id）中的一个分块数据（chunk）
#     修改其文档内容
#     :param dataset_id: 数据集ID
#     :param chunk_id: 分块数据ID
#     :param edit_chunk: 包含新内容的请求体
#     :return: 操作结果消息
#     """
#     # 加载向量数据库
#     vectorstore = load_vectorstore(dataset_id)

#     # 将 UUID 对象转换为字符串类型的 ID
#     str_chunk_id = str(chunk_id)

#     # 查询并获取指定 chunk
#     chunk = vectorstore.get(ids=[str_chunk_id])
#     print("chunk",chunk)
#     if not chunk["ids"]:
#         raise HTTPException(status_code=404, detail=f"Chunk with ID {chunk_id} not found in dataset {dataset_id}")
#     # 创建一个新的 Document 实例
#     page_content = edit_chunk.page_content
#     metadata = chunk['metadatas'][0]
#     metadata["chunk_word_count"] = len(edit_chunk.page_content)
#     update_chunk_document = Document(page_content=page_content, metadata=metadata)
#     # 修改指定的 chunk 内容
#     vectorstore.update_documents(ids=[str_chunk_id], documents=[update_chunk_document])

#     return {
#         "message": f"Chunk {chunk_id} has been edited in dataset {dataset_id}",
#         "updated_chunk": update_chunk_document
#     }


# QueryTestHistory有关的路由
# 定义 Pydantic 模型用于请求体验证
class QueryTestHistoryCreate(BaseModel):
    dataset_id: UUID
    query: str
    k: int
    min_relevance: float


# 定义 Pydantic 模型用于响应体验证
class QueryTestHistoryResponse(BaseModel):
    id: UUID
    dataset_id_id: UUID
    query: str
    k: int
    min_relevance: float
    created_at: str

    @validator("created_at", pre=True)
    def format_datetime(cls, value):
        return value.strftime("%Y-%m-%d %H:%M:%S")


# 获取指定 database_id 的所有 QueryTestHistory 的路由
@dataset_router.get(
    "/{database_id}/query-test-history/",
    response_model=List[QueryTestHistoryResponse],
    tags=["dataset"],
)
async def get_query_test_histories(database_id: str):
    """
    根据指定的databaseID获取查询测试历史记录
    :param database_id: 数据库ID
    :return: 查询测试历史记录列表
    """
    histories = (
        await QueryTestHistory.filter(dataset_id_id=database_id)
        .order_by("-created_at")
        .all()
    )
    return histories


# 创建新的 QueryTestHistory 的路由
@dataset_router.post(
    "/query-test-history", response_model=QueryTestHistoryResponse, tags=["dataset"]
)
async def create_query_test_history(query_test_history: QueryTestHistoryCreate):
    """
    创建一个新的查询测试历史记录
    :param query_test_history: 查询测试历史记录信息
    :return: 创建的数据库记录
    """
    dataset = await DataSet.get_or_none(id=query_test_history.dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    print("dataset", dataset)
    # 创建新的查询测试历史记录，并明确传递 dataset 对象
    new_query_test_history = await QueryTestHistory.create(
        dataset_id=dataset,
        query=query_test_history.query,
        k=query_test_history.k,
        min_relevance=query_test_history.min_relevance,
    )
    return new_query_test_history


# 删除指定 QueryTestHistory 的路由
@dataset_router.delete(
    "/query-test-history/{query_test_history_id}", response_model=dict, tags=["dataset"]
)
async def delete_query_test_history(query_test_history_id: UUID):
    """
    删除一个查询测试历史记录
    :param query_test_history_id: 查询测试历史记录ID
    :return: 删除结果消息
    """
    query_test_history = await QueryTestHistory.get_or_none(id=query_test_history_id)
    if not query_test_history:
        raise HTTPException(status_code=404, detail="QueryTestHistory not found")

    # 删除数据库记录
    await query_test_history.delete()

    return {"message": f"QueryTestHistory {query_test_history_id} has been deleted."}
