from datetime import datetime, timedelta, timezone
from typing import Union
import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel
from models.models import AdminUser
import bcrypt
from enum import Enum

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24  # jwt exp: 24小时

# 表示登录认证会通过这个路径来获取 token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/admin")


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

invalid_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect username or password",
    headers={"WWW-Authenticate": "Bearer"},
)


# 定义枚举类型
class RoleEnum(str, Enum):
    admin = "admin"
    user = "user"


# 封装 token output 信息
class TokenOutputModel(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenEncodeDataModel(BaseModel):
    username: Union[str, None] = None
    role: RoleEnum = RoleEnum.user


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


async def authenticate_admin_user(username: str, password: str = None):
    admin_user = await AdminUser.get_or_none(username=username)
    if not admin_user:
        raise invalid_credentials_exception
    # 如果密码为空，则不验证密码，用于验证 token，密码不为空则验证密码，用于登录校验
    if password is not None and not verify_password(
        password, admin_user.hashed_password
    ):
        raise invalid_credentials_exception
    return admin_user


def create_access_token(
    encode_data: TokenEncodeDataModel, expires_delta: Union[timedelta, None] = None
):
    to_encode = {"sub": encode_data.username, "role": encode_data.role}
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    # create_access_token 函数中生成 JWT 时，添加了 "exp" 字段，该字段定义了 token 的过期时间。
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# 这里的 token 是从请求的 Authorization header 中获取的
async def get_current_admin_user_dependence(token: str = Depends(oauth2_scheme)):
    try:
        # JWT 的标准实现会在解码时自动检查 "exp" 字段，并在 token 过期时抛出异常。
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        print(f"username: {username}")
        if username is None:
            raise credentials_exception
    except Exception as e:
        print(f"e: {e}")
        raise credentials_exception
    user = await authenticate_admin_user(username=username)
    if user is None:
        raise credentials_exception
    return user
