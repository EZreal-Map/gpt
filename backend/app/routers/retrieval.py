from fastapi import APIRouter, UploadFile, HTTPException, Query
from pathlib import Path
import shutil
from utils.retrieval import PDF_to_documents, load_vectorstore
from models.models import Article
from uuid import UUID
from pydantic import BaseModel
from langchain.docstore.document import Document

# 创建一个APIRouter实例，用于管理与数据集相关的API路由
retrieval_router = APIRouter()

# 定义文件目录路径
document_dir = Path("static/document")  # 用于存储文档文件的目录
temp_dir = Path("static/temp")  # 用于临时存储上传文件的目录

# 创建 static/document 和 static/temp 文件夹，如果不存在则创建
document_dir.mkdir(parents=True, exist_ok=True)
temp_dir.mkdir(parents=True, exist_ok=True)

# 定义函数，用于清空 temp_dir 目录中的所有文件
def clear_temp_dir():
    for temp_file in temp_dir.iterdir():
        if temp_file.is_file():
            temp_file.unlink()  # 删除文件

# API 路由，用于清空 temp_dir 目录
@retrieval_router.post("/clear-temp-dir/")
async def clear_temp_directory():
    """
    清空 temp_dir 目录中的所有文件
    :return: 成功清空目录的消息
    """
    clear_temp_dir()
    return {"message": "Temporary directory cleared successfully."}

# API 路由，用于上传文件
@retrieval_router.post("/uploadfiles/")
async def create_upload_files(file: list[UploadFile]):
    """
    上传文件并将其保存到 temp_dir 目录
    :param file: 要上传的文件列表
    :return: 上传文件的文件名列表
    """
    filenames = []
    for f in file:
        temp_file_path = temp_dir / f.filename  # 定义文件保存路径

        # 保存文件到 temp_dir 目录
        with temp_file_path.open("wb") as buffer:
            shutil.copyfileobj(f.file, buffer)

        filenames.append(f.filename)  # 添加文件名到列表
    return {"filenames": filenames}

# API 路由，用于删除指定文件
@retrieval_router.delete("/deletetempfile/{filename}")
async def delete_file(filename: str):
    """
    删除 temp_dir 目录中的指定文件
    :param filename: 要删除的文件名
    :return: 删除文件的消息
    :raise HTTPException: 如果文件不存在，则抛出404错误
    """
    file_path = temp_dir / filename  # 定义文件路径
    if file_path.exists():
        file_path.unlink()  # 删除文件
        return {
            "message": f"{filename} 删除成功",
            "filename": filename
        }
    else:
        raise HTTPException(status_code=404, detail=f"{filename}文件不存在")

# API 路由，用于获取 temp_dir 目录中的所有 PDF 文件并进行处理
@retrieval_router.get("/temp-pdf-files-chunks/")
async def get_temp_pdf_files(chunk_size: int = Query(default=500, ge=0), 
                        chunk_overlap: int = Query(default=100, ge=0), 
                        separator: str = Query(default="")):
    """
    获取 temp_dir 目录中的所有 PDF 文件，并将其转换为文档内容
    :param chunk_size: 每个文档块的大小
    :param chunk_overlap: 每个文档块的重叠大小
    :param separator: 文档块之间的分隔符
    :return: 转换后的文档内容
    """
    # 获取 temp_dir 目录中的所有 PDF 文件
    pdf_files = list(temp_dir.glob("*.pdf"))
    # 将 PDF 文件转换为文档内容
    documents = PDF_to_documents(pdf_files, chunk_size, chunk_overlap, separator)
    return documents

@retrieval_router.get("/{dataset_id}/similarity-search")
async def similarity_search(dataset_id: UUID, 
                            query: str = Query(..., description="The query text to search for"), 
                            k: int = Query(4, description="The number of similar chunks to return"), 
                            min_relevance: float = Query(0.5, description="The minimum relevance score to return")):
    """
    查询指定数据集（dataset_id）中与查询文本（query）最相似的分块数据（chunks）
    
    :param dataset_id: 数据集ID
    :param query: 查询文本
    :return: 查询到的相关分块数据列表
    """
    # 加载向量数据库
    vectorstore = load_vectorstore(dataset_id)

    # 使用similarity_search_with_score查询相关chunks
    try:
        docs_and_scores = vectorstore.similarity_search_with_score(query=query, k=k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # # 构造返回结果
    # results = [
    #     Chunk(id=doc.id, content=doc.content, score=score) 
    #     for doc, score in docs_and_scores
    # ]
    print(docs_and_scores[0][1])
    
    # 原来的分数是相似度，现在将其转换为1减去相似度，List[Tuple[Document, float]]
    # 构造新的结果列表，将分数转换为1减去原始分数
    modified_docs_and_scores = [
        {
        "document":doc,
        "score": 1 - score
        } for doc, score in docs_and_scores if 1-score >= min_relevance
    ]

    return modified_docs_and_scores

class EditChunkDocument(BaseModel):
    page_content: str

@retrieval_router.put("/{dataset_id}/edit-chunk")
async def edit_chunk_by_metadata_id(dataset_id: UUID, 
                           edit_chunk: EditChunkDocument,
                           metadata_id: UUID = Query(..., description="Chunk document metadata ID to edit")
                           ):
    """
    编辑特定数据集（dataset_id）中的一个分块数据（chunk）
    修改其文档内容
    :param dataset_id: 数据集ID
    :param chunk_id: 分块数据ID
    :param edit_chunk: 包含新内容的请求体
    :return: 操作结果消息
    """
    # 加载向量数据库
    vectorstore = load_vectorstore(dataset_id)

    # 将 UUID 对象转换为字符串类型的 ID
    str_metadata_id = str(metadata_id)

    # 查询并获取指定 chunk
    chunk = vectorstore.get(where={"document_metadata_id": str_metadata_id})

    # print("chunk",chunk)
    if not chunk["ids"]:
        raise HTTPException(status_code=404, detail=f"Chunk with ID {metadata_id} not found in dataset {dataset_id}")
    # 创建一个新的 Document 实例
    page_content = edit_chunk.page_content
    metadata = chunk['metadatas'][0]
    metadata["chunk_word_count"] = len(edit_chunk.page_content)
    update_chunk_document = Document(page_content=page_content, metadata=metadata)
    # 修改指定的 chunk 内容
    vectorstore.update_documents(ids=chunk["ids"], documents=[update_chunk_document])

    return {
        "message": f"Chunk {metadata_id} has been edited in dataset {dataset_id}",
        "updated_chunk": update_chunk_document
    }


# 删除指定chunk块，通过 chunk_id
@retrieval_router.delete("/{dataset_id}/delete-chunk")
async def delete_chunk_by_metadata_id(dataset_id: UUID, 
                             article_id: UUID = Query(None, description="Article ID for updating chunk_sum_num"),
                             metadata_id: UUID = Query(..., description="Chunk document metadata ID to delete")
                             ):
    """
    删除特定数据集（dataset_id）中的一个分块数据（chunk）
    同时更新相关的文章（article）的 chunk_sum_num 属性
    :param dataset_id: 数据集ID
    :param chunk_id: 分块数据ID
    :param article_id: 文章ID，用于更新 chunk_sum_num
    :return: 操作结果消息
    """
    # 加载向量数据库
    vectorstore = load_vectorstore(dataset_id)

    # 将 UUID 对象转换为字符串类型的 ID
    str_metadata_id = str(metadata_id)
    # 查询并获取指定 chunk
    chunk = vectorstore.get(where={"document_metadata_id": str_metadata_id})
    
    if not chunk["ids"]:
        raise HTTPException(status_code=404, detail=f"Chunk with ID {str_metadata_id} not found in dataset {dataset_id}")

    # 删除指定的 chunk
    vectorstore.delete(chunk["ids"])

    # 更新文章的 chunk_sum_num
    if article_id:
        article = await Article.get_or_none(id=article_id)
        if article:
            article.chunk_sum_num -= 1
            await article.save()

    return {
        "message": f"Chunk {chunk['ids']} has been deleted from dataset {dataset_id}",
        "chunk_deleted": chunk,
        "article.chunk_sum_num": article.chunk_sum_num
    }