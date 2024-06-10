from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langserve import add_routes
from fastapi import APIRouter

from dotenv import load_dotenv
# 加载 .env 文件中的环境变量
load_dotenv()
chat_router = APIRouter()

model = ChatOpenAI(model="gpt-3.5-turbo-0125")

prompt = ChatPromptTemplate.from_template("tell me a joke about {topic}")
add_routes(
    chat_router,
    prompt | model,
    path="/joke",
)