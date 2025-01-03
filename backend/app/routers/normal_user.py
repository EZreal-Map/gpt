from fastapi import APIRouter, HTTPException, Query, UploadFile, Body
from pydantic import BaseModel, validator
from tortoise.exceptions import IntegrityError
from models.models import NormalUser, UserGroup, NormalUserGroup
from utils.authenticate import hash_password
from datetime import datetime
from tortoise.transactions import in_transaction
from typing import Union, Optional, List, Dict
import pandas as pd
import io
import math


# 创建一个 APIRouter 实例
normal_user_router = APIRouter()

DEFAULT_PASSWORD = "123456"


class ResultModel(BaseModel):
    code: int = 0  # 编码：1成功，0和其它数字为失败
    message: str = "success"
    data: Optional[Union[List, Dict]] = None  # 支持空值、列表、字典


# Pydantic 模型用于数据验证
class NormalUserCreate(BaseModel):
    user_id: str
    name: str
    password: str = DEFAULT_PASSWORD
    groups: list[str] = []


class NormalUserOutput(BaseModel):
    user_id: str
    name: str
    updated_at: str  # 这里定义的还是字符串类型，用于存储格式化后的时间
    groups: list[str]

    # 使用 @validator 来格式化 `updated_at` 字段
    @validator("updated_at", pre=True)
    def format_updated_at(cls, v):
        if isinstance(v, datetime):
            return v.strftime("%Y-%m-%d %H:%M:%S")  # 格式化为字符串
        return v  # 如果已经是字符串，不做处理


# 创建一个用户
@normal_user_router.post(
    "/normal_user/", response_model=ResultModel, tags=["normal_user"]
)
async def create_normal_user(user: NormalUserCreate):
    try:
        async with in_transaction():
            hashed_password = hash_password(user.password)
            user_obj = await NormalUser.create(
                user_id=user.user_id, name=user.name, hashed_password=hashed_password
            )
            for name in user.groups:
                # 创建用户组
                # get_or_create 返回一个tuple 第一个元素是对象，第二个元素是是否创建了新对象
                user_group = await UserGroup.get_or_create(name=name)
                print(user_group[1])
                # 创建用户与用户组的关系
                await NormalUserGroup.create(user=user_obj, group=user_group[0])
            return ResultModel(message="新增用户成功")
    except IntegrityError as e:
        # 检查错误信息是否包含重复主键的相关信息
        if "Duplicate entry" in str(e):
            return ResultModel(
                code=1,
                message=f"创建失败，用户编号 '{user.user_id}' 已经存在。",
            )


# 接收csv/xls/xlsx文件，批量创建用户
@normal_user_router.post("/normal_user/uploadfile/", tags=["fileset"])
async def batch_create_normal_users(file: UploadFile):
    async with in_transaction() as conn:
        # 用pandas读取文件内容
        content = await file.read()
        # 如果是csv文件，使用pd.read_csv读取
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.StringIO(content.decode("utf-8")))
        # 如果是xls或xlsx文件，使用pd.read_excel读取
        elif file.filename.endswith(".xls") or file.filename.endswith(".xlsx"):
            df = pd.read_excel(io.BytesIO(content))
        else:
            return ResultModel(
                code=1, message="文件格式不正确，只支持csv、xls、xlsx格式。"
            )
        # 遍历每一行，创建用户
        # 检查如果有3列，就按照user_id、name、groups的顺序读取
        if len(df.columns) == 3:
            for index, row in df.iterrows():
                # 判断非空
                if (
                    pd.isnull(row.iloc[0])
                    or pd.isnull(row.iloc[1])
                    or pd.isnull(row.iloc[2])
                ):
                    # 执行某个行失败时，回滚批量添加事务
                    await conn.rollback()
                    return ResultModel(code=1, message="创建失败，文件中有空值")
                user = NormalUserCreate(
                    user_id=row.iloc[0],
                    name=row.iloc[1],
                    groups=row.iloc[2].split(","),
                )
                result = await create_normal_user(user)
                # 如果创建失败，直接返回错误信息
                if result.code == 1:
                    # 执行某个行失败时，回滚批量添加事务
                    await conn.rollback()
                    return result
            return ResultModel(message="批量创建用户成功")
        # 如果有4列，就按照user_id、name、password、groups的顺序读取
        elif len(df.columns) == 4:
            for index, row in df.iterrows():
                # 判断非空
                if (
                    pd.isnull(row.iloc[0])
                    or pd.isnull(row.iloc[1])
                    or pd.isnull(row.iloc[2])
                    or pd.isnull(row.iloc[3])
                ):
                    # 执行某个行失败时，回滚批量添加事务
                    await conn.rollback()
                    return ResultModel(code=1, message="文件中有空值")
                user = NormalUserCreate(
                    user_id=row.iloc[0],
                    name=row.iloc[1],
                    password=row.iloc[2],
                    groups=row.iloc[3].split(","),
                )
                result = await create_normal_user(user)
                # 如果创建失败，直接返回错误信息
                if result.code == 1:
                    # 执行某个行失败时，回滚批量添加事务
                    await conn.rollback()
                    return result
            return ResultModel(message="批量创建用户成功")
        else:
            return ResultModel(
                code=1, message="文件列数不正确，要么是3列（使用默认密码），要么是4列。"
            )


# 删除一个用户
@normal_user_router.delete(
    "/normal_user/", response_model=ResultModel, tags=["normal_user"]
)
async def delete_normal_user(user_id_list: List[str] = Body(...)):
    for user_id in user_id_list:
        user_obj = await NormalUser.get_or_none(user_id=user_id)
        if user_obj is None:
            raise HTTPException(status_code=404, detail="User not found")
        await user_obj.delete()
    return ResultModel(message="删除用户成功")


class NormalUserUpdate(BaseModel):
    new_user_id: str
    name: str
    is_reset_password: bool
    groups: list[str]


# 更新一个用户
@normal_user_router.put(
    "/normal_user/{original_user_id}", response_model=ResultModel, tags=["normal_user"]
)
async def update_normal_user(update_user: NormalUserUpdate, original_user_id: str):
    try:
        async with in_transaction():
            user_obj = await NormalUser.get_or_none(user_id=original_user_id)
            if user_obj is None:
                raise HTTPException(status_code=404, detail="User not found")
            # 1、更新 NormalUserGroup 表
            # 删除原有的用户组关系
            await NormalUserGroup.filter(user=user_obj).delete()
            # 创建新的用户组关系
            for name in update_user.groups:
                user_group = await UserGroup.get_or_create(name=name)
                await NormalUserGroup.create(user=user_obj, group=user_group[0])
            # 2、更新 NormalUser 表中的name和hashed_password字段
            user_obj.user_id = update_user.new_user_id
            user_obj.name = update_user.name
            if update_user.is_reset_password:
                user_obj.hashed_password = hash_password(DEFAULT_PASSWORD)
            await user_obj.save()
        return ResultModel(message="更新用户成功")
    except IntegrityError as e:
        # 检查错误信息是否包含重复主键的相关信息
        if "Duplicate entry" in str(e):
            return ResultModel(
                code=1,
                message=f"更新失败，用户编号 '{update_user.new_user_id}' 已经存在。",
            )


# 获取所有用户及其所属的组
@normal_user_router.get(
    "/normal_user/", response_model=ResultModel, tags=["normal_user"]
)
async def get_normal_users(
    name: str = Query(None),
    group: str = Query(None),
    page_num: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1),
):
    # 获取所有用户及其所属的组
    # 关联 NormalUser, NormalUserGroup, UserGroup 三个表
    # "__" 代表2个表字段分割
    # user_groups：从 NormalUser 中获取到所有与该用户关联的 NormalUserGroup 对象。
    # group：从每个 NormalUserGroup 中获取到对应的 UserGroup 对象。
    # users = await NormalUser.all().prefetch_related("user_groups__group")

    query = NormalUser.all().prefetch_related("user_groups__group").order_by("user_id")
    # 然后使用 filter 进行条件筛选
    if name:
        query = query.filter(name__icontains=name)  # 直接使用字段名，而不是通过模型访问
    if group:
        # 如果提供了 group 参数，按组名进行筛选
        query = query.filter(user_groups__group__name=group)
    # 分页功能
    # 1.获取总用户数
    total_user_num = await query.count()
    # 向上取整
    total_page_num = math.ceil(total_user_num / page_size)
    # 当条件查询为 0 个的时候，会出现 total_page_num 为 0 的情况，这时候需要设置为 1
    if total_page_num == 0:
        total_page_num = 1
    if page_num > total_page_num:
        page_num = total_page_num
    # 2.添加分页功能：`offset` 是起始位置，`limit` 是返回条数
    page_start = (page_num - 1) * page_size
    query = query.offset(page_start).limit(page_size)
    # 执行查询
    users = await query
    # 拼接 NormalUser 和 UserGroup 的信息
    result = []
    for user in users:
        groups = [user_group.group.name for user_group in user.user_groups]
        result.append(
            NormalUserOutput(
                user_id=user.user_id,
                name=user.name,
                updated_at=user.updated_at,
                groups=groups,
            )
        )
    data = {"total_page_num": total_page_num, "users": result}
    return ResultModel(data=data)


# 获取所有用户组
@normal_user_router.get("/group/", response_model=ResultModel, tags=["group"])
async def get_user_groups():
    groups = await UserGroup.all().order_by("-updated_at")
    return ResultModel(data=[group.name for group in groups])
