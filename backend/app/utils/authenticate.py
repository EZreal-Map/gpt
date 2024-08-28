from datetime import datetime, timedelta, timezone
from typing import Union
import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel
from models.models import AdminUser
import bcrypt

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24  # jwt exp: 24小时

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# 封装 token output 信息
class TokenModel(BaseModel):
    access_token: str
    token_type: str


class TokenDataModel(BaseModel):
    username: Union[str, None] = None


class UserModel(BaseModel):
    username: str
    password: str


# 区别 UserModel 在于把password -> hashed_password
class UserInDBModel(BaseModel):
    username: str
    hashed_password: str


# 使用 bcrypt 对密码进行哈希
def hash_password(password):
    # 将密码转换为字节格式
    pwd_bytes = password.encode("utf-8")
    # 生成盐值，bcrypt 会自动生成一个安全的随机盐
    salt = bcrypt.gensalt()
    # 使用生成的盐对密码进行哈希
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password


# 检查提供的密码是否与存储的哈希密码匹配
def verify_password(plain_password, hashed_password):
    # 将明文密码转换为字节格式
    password_byte_enc = plain_password.encode("utf-8")
    # 确保存储的哈希密码也是字节格式
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode("utf-8")
    # 验证密码，bcrypt.checkpw 会自动从 hashed_password 中提取盐
    return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_password)


def get_user(users_db, username: str):
    for user in users_db:
        if user.username == username:
            return user


def authenticate_user(users_db, username: str, password: str):
    user = get_user(users_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    # create_access_token 函数中生成 JWT 时，添加了 "exp" 字段，该字段定义了 token 的过期时间。
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # JWT 的标准实现会在解码时自动检查 "exp" 字段，并在 token 过期时抛出异常。
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenDataModel(username=username)
    except InvalidTokenError:
        raise credentials_exception
    users_db = await AdminUser.all()
    user = get_user(users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


# 不通过依赖项函数，直接在路由函数中验证用户是否登录，这样不会返回 401 错误，而是返回 True 或 False
async def is_user_logged_in(request: Request) -> bool:
    authorization: str = request.headers.get("Authorization")
    if authorization is None or not authorization.lower().startswith("bearer "):
        return False
    token = authorization.split(" ")[1]
    try:
        # 解码 JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        print(f"username: {username}")
        if username is None:
            return False
        token_data = TokenDataModel(username=username)
    except:
        # exp 过期
        return False

    users_db = await AdminUser.all()
    user = get_user(users_db, username=token_data.username)
    if user is None:
        return False

    return True
