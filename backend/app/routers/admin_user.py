from fastapi import APIRouter, HTTPException, Depends, Request, Body
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from models.models import AdminUser, NormalUser, APPSet, GroupAPPSet, NormalUserGroup
from pydantic import BaseModel
from utils.authenticate import (
    UserModel,
    UserInDBModel,
    TokenEncodeDataModel,
    RoleEnum,
    ACCESS_TOKEN_EXPIRE_HOURS,
    hash_password,
    authenticate_admin_user,
    authenticate_normal_user,
    create_access_token,
    get_current_admin_user_dependence,
    get_current_normal_user_dependence,
)
from routers.normal_user import ResultModel
from routers.appset import PrivacyEnum

# 创建一个APIRouter实例
admin_user_router = APIRouter()


# 创建一个admin用户
@admin_user_router.post("/admin-user", tags=["admin_user"])
async def create_admin_user(user: UserModel):
    """
    创建一个admin用户
    :param user: 用户信息
    :return: 创建的用户信息
    """
    # 创建新的数据集记录
    hashed_password = hash_password(user.password)
    user_in_db = UserInDBModel(username=user.username, hashed_password=hashed_password)
    try:
        new_user = await AdminUser.create(**user_in_db.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return new_user


# 获取所有admin用户
@admin_user_router.get("/admin-user", tags=["admin_user"])
async def get_admin_users():
    """
    获取所有admin用户
    :return: 所有admin用户信息
    """
    # 获取所有数据集记录
    users = await AdminUser.all()
    return users


# 删除一个admin用户
@admin_user_router.delete("/admin-user/{username}", tags=["admin_user"])
async def delete_admin_user(username: str):
    """
    删除一个admin用户
    :param username: 用户名
    :return: 删除的用户信息
    """
    # 查询指定的用户
    user = await AdminUser.get_or_none(username=username)
    if not user:
        raise HTTPException(status_code=404, detail="未找到指定的用户")

    # 删除用户
    await user.delete()
    return {"detail": f"用户:{username}删除成功"}


# 封装 token output 信息
class TokenOutputModel(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: RoleEnum = RoleEnum.USER
    name: str  # 区别于username，这里是用户的真实姓名（normal_user才有这个属性，admin_user这个属性和username是同一个）


# 用户登录 / 用户身份认证(depend)，获取 token / 更新 token
@admin_user_router.post("/login", tags=["login"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # 先验证是否是admin用户
    user = await authenticate_admin_user(form_data.username, form_data.password)
    if user:
        role = RoleEnum.ADMIN
        name = user.username
        username = user.username
    else:
        # 再验证是否是normal用户
        user = await authenticate_normal_user(form_data.username, form_data.password)
        if not user:
            return ResultModel(code=1, message="用户名或密码错误")
        role = RoleEnum.USER
        name = user.name
        username = user.user_id
    access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    # 生成 token, 放入 sub:username role:admin/和 exp:ACCESS_TOKEN_EXPIRE_HOURS
    encode_data = TokenEncodeDataModel(username=username, role=role)
    access_token = create_access_token(
        encode_data=encode_data, expires_delta=access_token_expires
    )
    return ResultModel(
        data=TokenOutputModel(access_token=access_token, role=role, name=name)
    )


# 不依赖oauth2_scheme依赖项，验证用户是否登录，不会触发401错误，只返回是否登录
# 给前端使用： 判断用户是否登录，比直接判断是否保存userStore.username为空要更加准确，因为后端可以多判断token是否过期
@admin_user_router.get("/login/is_admin_login", tags=["login"])
async def check_user_logged_in(request: Request):
    """
    验证用户是否登录
    :param request: FastAPI Request 对象
    :return: 是否登录
    """
    try:
        token = request.headers.get("Authorization").split(" ")[1]
        await get_current_admin_user_dependence(token=token)
    except Exception:
        return {"is_login": False}
    return {"is_login": True}


@admin_user_router.get("/login/is_normal_login", tags=["login"])
async def check_user_logged_in(request: Request):
    """
    验证用户是否登录
    :param request: FastAPI Request 对象
    :return: 是否登录
    """
    try:
        token = request.headers.get("Authorization").split(" ")[1]
        user = await get_current_normal_user_dependence(token=token)
    except Exception:
        return {"is_login": False}
    return {"is_login": True}


@admin_user_router.get("/login/is_normal_user_access_app/", tags=["login"])
async def check_user_logged_in(request: Request, appid: str = Body(None)):
    """
    验证用户是否登录
    :param request: FastAPI Request 对象
    :return: 是否登录
    """
    try:
        token = request.headers.get("Authorization").split(" ")[1]
        user = await get_current_normal_user_dependence(token=token)
        if appid is None and user:
            # 如果appid为空，不代表要验证是否有权限访问app，只是验证是否登录
            return {"is_login": True}
        # 如果是NormalUser，判断是否有权限访问该app，AdminUser不需要判断
        if isinstance(user, NormalUser):
            # 判断用户是否有权限访问该app
            # 通过appid查询APPSet表
            appset = await APPSet.get_or_none(id=appid)
            # 如果appset的privacy是PRIVATE，直接返回False
            if appset.privacy == PrivacyEnum.PRIVATE:
                return {"is_login": False}
            # 通过user_id查询NormalUser表
            normal_user = await NormalUser.get_or_none(user_id=user.user_id)
            # 通过normal_user查询NormalUserGroup表
            groups = await NormalUserGroup.filter(user=normal_user)
            for group in groups:
                # 通过group和appset查询GroupAPPSet表
                group_app_set = await GroupAPPSet.get_or_none(
                    app_id=appid, group_id=group.group_id
                )
                if group_app_set:
                    return {"is_login": True}
            # 循环结束，没有找到匹配的GroupAPPSET，返回False
            return {"is_login": False}
    except Exception as e:
        print("error:", e)
        return {"is_login": False}
    return {"is_login": True}
