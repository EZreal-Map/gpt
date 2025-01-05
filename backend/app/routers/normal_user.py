from fastapi import APIRouter, HTTPException, Query, UploadFile, Body, status, Depends
from pydantic import BaseModel, validator
from tortoise.exceptions import IntegrityError
from models.models import (
    NormalUser,
    UserGroup,
    NormalUserGroup,
    APPSet,
    GroupAPPSet,
    ChatSet,
)
from routers.chatset import delete_chatset_by_chatset
from utils.authenticate import hash_password, get_current_normal_user_dependence
from routers.appset import APPSetResponseModel, PrivacyEnum
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
    code: int = 0  # 编码：0成功，1失败
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
        # 删除NormalUser表中的用户
        user_obj = await NormalUser.get_or_none(user_id=user_id)
        if user_obj is None:
            raise HTTPException(status_code=404, detail="User not found")
        await user_obj.delete()
        # 删除NormalUserGroup表中的用户组关系（自动删除）
        # 删除ChatSet表中的用户关联
        chatsets = await ChatSet.filter(user_id=user_obj.id)
        for chatset in chatsets:
            await delete_chatset_by_chatset(chatset)

    return ResultModel(message="删除用户成功")


# 更新一个用户密码
# 路径没办法加入/update,因为不这样会导致与 "更新一个用户" 路径冲突
@normal_user_router.put(
    "/normal_user/password/update", response_model=ResultModel, tags=["normal_user"]
)
async def update_normal_user_password(
    user=Depends(get_current_normal_user_dependence), password: str = Body(...)
):
    user_obj = await NormalUser.get_or_none(id=user.id)
    if user_obj is None:
        return ResultModel(
            code=1, message="无法修改密码：用户信息未找到，请尝试重新登录后重试"
        )
    user_obj.hashed_password = hash_password(password)
    await user_obj.save()
    return ResultModel(message="修改密码成功，请重新登录")


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


# 通过用户编号获取与之关联的应用（APPSet）信息
# 异步查询 ChatSet 中与 user_id 相关的记录，去重 app_id 并获取与之关联的 APPSet 信息
@normal_user_router.get(
    "/normal_user/appset/", response_model=ResultModel, tags=["normal_user"]
)
async def get_user_appset(user_id: str = Query(...)):
    # 查询 NormalUser
    user = await NormalUser.filter(user_id=user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    # 通过 NormalUser 获取关联的 UserGroup
    user_groups = await NormalUserGroup.filter(user=user).select_related("group").all()
    # 获取所有关联的 APPSet
    app_sets = set()  # 使用集合来去重 APPSet 实例
    for user_group in user_groups:
        # 获取与 UserGroup 关联的 APPSet
        group_apps = (
            await GroupAPPSet.filter(group=user_group.group).select_related("app").all()
        )
        for group_app in group_apps:
            app_sets.add(group_app.app)  # 将 APPSet 实例加入集合，避免重复
    # 组织返回数据
    data = []
    for app_set in app_sets:
        if app_set.privacy == PrivacyEnum.PRIVATE:
            continue
        data.append(
            APPSetResponseModel(
                id=app_set.id,
                name=app_set.name,
                description=app_set.description,
                privacy=app_set.privacy,
                created_at=app_set.created_at,
            )
        )
    return ResultModel(data=data)


# 获取所有用户组
@normal_user_router.get("/group/", response_model=ResultModel, tags=["group"])
async def get_user_groups():
    groups = await UserGroup.all().order_by("-updated_at")
    return ResultModel(data=[group.name for group in groups])


# 获取所有用户组及其用户数量
@normal_user_router.get("/group/usercount/", response_model=ResultModel, tags=["group"])
async def get_user_groups_usercount():
    # 获取所有用户组并计算每个组的用户数量
    groups = await UserGroup.all().order_by("-updated_at")
    result = []
    for group in groups:
        # 统计每个组的用户数量
        user_count = await NormalUserGroup.filter(group=group).count()
        result.append(
            {"id": group.id, "group_name": group.name, "user_count": user_count}
        )
    return ResultModel(data=result)


# 根据group_id更新用户组名称
@normal_user_router.put("/group/{group_id}", response_model=ResultModel, tags=["group"])
async def update_user_group_name(group_id: str, newname: str = Body(...)):
    # 检查用户组名称是否重名
    group = await UserGroup.get_or_none(name=newname)
    if group is not None:
        return ResultModel(
            code=1, message="修改失败：该用户组名称已被占用，请选择一个不同的名称"
        )
    # 获取即将修改的用户组
    group = await UserGroup.get_or_none(id=group_id)
    if group is None:
        ResultModel(code=1, message="修改失败，用户组不存在，请刷新页面后重试")
    group.name = newname
    await group.save()
    return ResultModel(message="用户组名称更新成功，新名称已生效")


# 根据group_id删除用户组，同时删除仅与此用户组关联的用户
@normal_user_router.delete(
    "/group/{group_id}", response_model=ResultModel, tags=["group"]
)
async def delete_user_group(group_id: str):
    async with in_transaction():
        # 获取即将删除的用户组
        group = await UserGroup.get_or_none(id=group_id)
        if group is None:
            return ResultModel(code=1, message="删除失败，用户组不存在")
        # 删除仅与此用户组关联的用户
        # 1、查找仅与此用户组关联的用户
        user_group_sets = await NormalUserGroup.filter(group=group).all()
        # 2、删除这些与该用户组关联的用户
        for user_group in user_group_sets:
            user_id = user_group.user_id
            # 检查该用户是否仅与该组关联
            related_groups = await NormalUserGroup.filter(user_id=user_id).all()
            if len(related_groups) == 1:  # 仅与当前用户组关联
                await NormalUser.filter(id=user_id).delete()  # 删除用户
        # 删除用户组
        await group.delete()
        # 用户与用户组关联表（自动删除）,用户组与APP关联表（自动删除）
        # NormalUserGroup/GroupAPPSet 表中的记录会自动删除
    return ResultModel(message="用户组删除成功，同时清除了仅与该用户组关联的用户")


class GroupAPPBindModel(BaseModel):
    groups: list[str] = []
    appid: str


# 绑定用户组与APP
@normal_user_router.post("/group/appset/", response_model=ResultModel, tags=["group"])
async def bind_group_appset(groups_appid: GroupAPPBindModel):
    async with in_transaction():
        appset = await APPSet.get_or_none(id=groups_appid.appid)
        if appset is None:
            raise HTTPException(status_code=404, detail="APP not found")
        # 删除原有的用户组与APP的关系
        await GroupAPPSet.filter(app=appset).delete()
        # 创建新的用户组与APP的关系
        if len(groups_appid.groups) == 0:
            return ResultModel(message="用户分组与应用解绑成功")
        for group_name in groups_appid.groups:
            user_group = await UserGroup.get_or_none(name=group_name)
            if user_group is None:
                raise HTTPException(status_code=404, detail="Group not found")
            await GroupAPPSet.create(group=user_group, app=appset)
    return ResultModel(message="用户分组与应用绑定成功")


# 获取用户组与APP的绑定关系
@normal_user_router.get("/group/appset/", response_model=ResultModel, tags=["group"])
async def get_group_appset(appid: str):
    appset = await APPSet.get_or_none(id=appid)
    if appset is None:
        raise HTTPException(status_code=404, detail="APP not found")
    # 查询与该 APP 关联的 GroupAPPSet，并加载关联的 group 数据
    group_appsets = await GroupAPPSet.filter(app=appset).prefetch_related("group")
    # 提取 group 的名称
    groups = [group_appset.group.name for group_appset in group_appsets]
    return ResultModel(data=groups)
