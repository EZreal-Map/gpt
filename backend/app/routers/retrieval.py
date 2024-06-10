from fastapi import APIRouter, UploadFile, HTTPException, Query
from pathlib import Path
import shutil
from utils.retrieval import PDF_to_documents
from models.models import DataSet, Article

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
@retrieval_router.delete("/deletefile/{filename}")
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
@retrieval_router.get("/pdf-files/")
async def get_pdf_files(chunk_size: int = Query(default=500, ge=0), 
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
