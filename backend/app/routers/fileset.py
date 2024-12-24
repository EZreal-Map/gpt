from fastapi import APIRouter, UploadFile, Header, Form, HTTPException
import pathlib
import shutil
from pydantic import BaseModel, Field
from utils.retrieval import PDF_to_documents, load_vectorstore
from tortoise.exceptions import DoesNotExist
from models.models import FileSet, File, ChatSet, APPSet
from tortoise.transactions import in_transaction  # 导入事务


# 创建一个APIRouter实例
fileset_router = APIRouter()

async def get_fileset(fileset_id: str):
    """
    通过 fileset_id 查询 File 表中的记录
    :param fileset_id: FileSet 的 ID
    :return: File 实例列表或空列表
    """
    print("fileset_id:", fileset_id)
    if not fileset_id:
        return []

    # 查询 File 表，获取与给定 fileset_id 关联的文件
    files = await File.filter(fileset_id=fileset_id).all()  # 使用 await

    # 如果查询结果为空，返回空列表
    if not files:
        return []

    # 返回文件列表，将每个文件对象转换为字典格式
    return [
        {
            "id": str(file.id),
            "name": file.filename,
            "create_time": file.create_time.isoformat() if file.create_time else None
        }
        for file in files
    ]

class QueryFilesetIDModel(BaseModel):
    appset_id: str = Field(..., description="APPSet的ID，确认模型参数与检索参数")
    chat_id: str = Field(None, description="ChatSet的ID，可选, 用来查询历史对话上下文")
    is_test_mode: bool = Field(False, description="是否为测试模式")


# 获取 fileset_id fileset 文件集合
@fileset_router.post("", tags=["fileset"])
async def get_fileset_id(query_body: QueryFilesetIDModel):

    # 如果 chat_id 为空，直接返回None
    if not query_body.chat_id:
        fileset_id = None
    else:
        # 查询 FileSet 根据 chat_id 查找
        fileset = await FileSet.filter(chat_id=query_body.chat_id).first()
        if fileset:
            fileset_id = fileset.id
        else:
            fileset_id = None

    # 如果是测试模式，直接返回 appset_id作为fileset_id
    if query_body.is_test_mode:
        fileset_id = query_body.appset_id
    
    # 获取 fileset 文件集合
    files = await get_fileset(fileset_id)

    return {"fileset_id": fileset_id, "files": files}

# 函数：关联 ChatSet 和 FileSet
async def associate_chatset_with_fileset(chatset_id: str, fileset_id: str):
    try:
        # 获取 ChatSet 和 FileSet 实例
        chatset = await ChatSet.get(id=chatset_id)
        fileset = await FileSet.get(id=fileset_id)

        # 将 ChatSet 和 FileSet 关联起来
        fileset.chat_id = chatset  # 设置 FileSet 的 chat_id 为 ChatSet 实例

        # 保存更新后的 FileSet
        await fileset.save()

        return True

    except DoesNotExist as e:
        # 没有fileset记录，所以不用关联，返回False，属于正常情况
        return False

# AssociateModel 用于接受请求体
class AssociateModel(BaseModel):
    chatset_id: str  # ChatSet ID
    fileset_id: str  # FileSet ID

@fileset_router.post("/associate_chatset", tags=["fileset"])
async def associate_chatset_to_fileset(query_body: AssociateModel):
    """
    将 ChatSet 与 FileSet 关联
    :param query_body: 请求体，包含 chatset_id 和 fileset_id
    """
    # 调用 associate_chatset_with_fileset 函数
    result = await associate_chatset_with_fileset(query_body.chatset_id, query_body.fileset_id)
    print("新聊天记录关联结果：", result)

    return {"result": result}


# API 路由，用于上传文件
# 定义 fileset_dir 存储文件的临时目录
fileset_dir = pathlib.Path("./static/fileset")

@fileset_router.post("/uploadfiles/", tags=["fileset"])
async def create_upload_files(file: list[UploadFile],fileset_id: str = Form(...),chatset_id: str = Form(...),appset_id: str = Form(None),is_test_mode: bool = Form(False)):
    """
    上传文件并将其保存到以 fileset_id 命名的文件夹
    :param file: 要上传的文件列表
    :param fileset_id: 用于创建文件夹的应用程序 ID
    # Form 表单中的字段
    """
    # 如果是测试模式，将 fileset_id 设置为 appset_id
    if is_test_mode:
        fileset_id = appset_id

    # 查询数据库中是否存在该 fileset_id 对应的 FileSet
    try:
        fileset = await FileSet.get(id=fileset_id)  # 通过 fileset_id 查询数据库

    except DoesNotExist:
        appset = await APPSet.get(id=appset_id)
        # 如果没有找到，创建一个新的 FileSet
        fileset = await FileSet.create(
            id=fileset_id,  # 使用传入的 fileset_id 创建新记录
            appset_id = appset
        )
    # 如果 chat_id_id 为空，且 chatset_id 不为空，关联 chatset_id 和 fileset_id
    print("fileset.chat_id_id:", fileset.chat_id_id)
    if (not fileset.chat_id_id) and chatset_id:
        result = await associate_chatset_with_fileset(chatset_id, fileset_id)
        print("关联结果：", result)

    # 确保以 fileset_id 创建的文件夹存在
    app_folder = fileset_dir / fileset_id
    app_folder.mkdir(parents=True, exist_ok=True)  # 创建文件夹，若已存在则跳过

    filenames = []
    pdf_files = []  # 用于存储文件路径列表
    file_ids = []  # 用于存储文件 ID 列表

    for f in file:
        temp_file_path = app_folder / f.filename  # 在 fileset_id 文件夹下创建文件路径

        # 保存文件到 fileset_id 文件夹
        with temp_file_path.open("wb") as buffer:
            shutil.copyfileobj(f.file, buffer)

        filenames.append(f.filename)  # 保存文件名到列表
        pdf_files.append(str(temp_file_path))  # 保存文件路径到 pdf_files 列表

        # 创建 File 记录，将文件与 FileSet 关联
        file = await File.create(
            filename=f.filename,
            fileset_id=fileset,  # 传递 fileset 实例，而不是 fileset.id
        )
        file_ids.append(file.id)  # 保存文件 ID 到列表

    # 使用 pdf_files 调用 PDF_to_documents 函数
    # 使用默认的切割方式切割 PDF 文件
    documents = PDF_to_documents(file_paths=pdf_files, dataset_id=fileset.id, file_ids=file_ids)
    
    # 通过 fileset_id 加载vectorstore, 没有则创建，
    vectorstore = load_vectorstore(fileset.id)
    vectorstore.add_documents(documents) 
    
    return {"fileset_id": fileset_id}



@fileset_router.delete("/{file_id}", tags=["fileset"])
async def delete_file_by_id(file_id: str):
    """
    删除指定 ID 的文件
    :param file_id: 要删除的文件 ID
    :return: 成功删除的响应
    """
    print("file_id:", file_id)
    try:
        # 开启事务
        async with in_transaction() as tx:
            # 查询文件并删除
            file = await File.get(id=file_id)
            fileset_id = file.fileset_id_id  # 获取文件集 ID
            await file.delete()

            # 加载向量数据库
            vectorstore = load_vectorstore(fileset_id)

            # 使用 `where` 参数进行过滤 metadata.article_id == file_id
            file_chunks = vectorstore.get(where={"article_id": file_id})
            # print("file_chunks:", len(file_chunks["ids"]))

            # 删除文档数据
            for chunk_id in file_chunks["ids"]:
                # 假设 vectorstore.delete() 可以删除特定文档数据
                # print(f"删除文档数据: {chunk_id}")
                vectorstore.delete(chunk_id)  # 删除文档数据

            # 事务中的所有操作成功时，自动提交
            return {"message": "文件删除成功"}

    except DoesNotExist:
        raise HTTPException(status_code=404, detail="文件未找到")
    except Exception as e:
        # 如果发生异常，事务将自动回滚
        print(f"删除文件时发生错误: {e}")
        raise HTTPException(status_code=500, detail="文件删除失败")