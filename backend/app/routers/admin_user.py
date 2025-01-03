from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from models.models import AdminUser
from utils.authenticate import (
    UserModel,
    UserInDBModel,
    TokenOutputModel,
    TokenEncodeDataModel,
    RoleEnum,
    ACCESS_TOKEN_EXPIRE_HOURS,
    hash_password,
    authenticate_admin_user,
    create_access_token,
    get_current_admin_user_dependence,
)

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
@admin_user_router.get("/admin-users", tags=["admin_user"])
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


# 用户登录 / 用户身份认证(depend)，获取 token / 更新 token
@admin_user_router.post("/login/admin", tags=["login"])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> TokenOutputModel:
    user = await authenticate_admin_user(form_data.username, form_data.password)

    access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    # print(f"access_token_expires: {access_token_expires}")
    # 生成 token, 放入 sub:username 和 exp:ACCESS_TOKEN_EXPIRE_HOURS
    encode_data = TokenEncodeDataModel(username=user.username, role=RoleEnum.admin)
    access_token = create_access_token(
        encode_data=encode_data, expires_delta=access_token_expires
    )
    return TokenOutputModel(access_token=access_token)


# 不依赖oauth2_scheme依赖项，验证用户是否登录，不会触发401错误，只返回是否登录
# 给前端使用： 判断用户是否登录，比直接判断是否保存userStore.username为空要更加准确，因为后端可以多判断token是否过期
@admin_user_router.get("/login/status", tags=["login"])
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
