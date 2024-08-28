from typing import List


class Config:
    # 调试模式
    # APP_DEBUG: bool = True
    # 项目信息
    VERSION: str = "0.0.1"
    PROJECT_NAME: str = "gpt"
    DESCRIPTION: str = "基于fastapi为后端的langchain项目"
    # 静态资源目录
    # STATIC_DIR: str = os.path.join(os.getcwd(), "static")
    # 跨域请求
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    TORTOISE_ORM = {
        "connections": {
            "default": {
                # 'engine': 'tortoise.backends.asyncpg',  PostgreSQL
                "engine": "tortoise.backends.mysql",  # MySQL or Mariadb
                "credentials": {
                    "host": "localhost",  # 开发环境
                    # 'host': 'mysql', # 生产环境
                    "port": "3306",
                    "user": "root",
                    "password": "1209",
                    "database": "gpt",
                    "minsize": 1,
                    "maxsize": 5,
                    "charset": "utf8mb4",
                    "echo": True,
                },
            },
        },
        "apps": {
            "models": {
                "models": ["models.models", "aerich.models"],  # 这里修改指定模型的位置
                "default_connection": "default",
            }
        },
        "use_tz": False,
        "timezone": "Asia/Shanghai",
    }

    CHROMA = {"host": "localhost", "port": 9786}  # 开发环境
    # CHROMA = {'host': 'chroma', 'port': 8000} # 生产环境


settings = Config()
