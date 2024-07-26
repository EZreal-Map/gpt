from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from models.models import AdminUser
from utils.authenticate import UserModel, UserInDBModel, TokenModel, ACCESS_TOKEN_EXPIRE_HOURS, \
    hash_password, authenticate_user, create_access_token, is_user_logged_in

# 创建一个APIRouter实例
user_router = APIRouter()

# 创建一个admin用户
@user_router.post("/admin-user", tags=["user"])
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
@user_router.get("/admin-users", tags=["user"])
async def get_admin_users():
    """
    获取所有admin用户
    :return: 所有admin用户信息
    """
    # 获取所有数据集记录
    users = await AdminUser.all()
    return users

# 删除一个admin用户
@user_router.delete("/admin-user/{username}", tags=["user"])
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
@user_router.post("/login", tags=["login"])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> TokenModel:
    users_db = await AdminUser.all()
    user = authenticate_user(users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    print(f"access_token_expires: {access_token_expires}")
    # 生成 token, 放入 sub:username 和 exp:ACCESS_TOKEN_EXPIRE_HOURS
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return TokenModel(access_token=access_token, token_type="bearer")


# 不依赖oauth2_scheme依赖项，验证用户是否登录，不会触发401错误，只返回是否登录
@user_router.get("/login", tags=["login"])
async def check_user_logged_in(request: Request):
    """
    验证用户是否登录
    :param request: FastAPI Request 对象
    :return: 是否登录
    """
    is_login = await is_user_logged_in(request)
    return {"is_login": is_login}


