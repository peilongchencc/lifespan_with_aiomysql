import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from dataform.dataform import StoreContent, FetchChatHistory
from dotenv import load_dotenv
from contextlib import asynccontextmanager
# 环境变量必须要在使用环境变量中配置前导入
load_dotenv("env_config/.env.local")
from database.mysql import mysqler
from utils.chat_history import insert_chat_history, fetch_chat_history

@asynccontextmanager
async def lifespan(app: FastAPI):
    """利用aiomysql创建mysql连接池"""
    await mysqler.create_connect_pool()
    yield
    """销毁mysql连接池"""
    await mysqler.disconnect()

app = FastAPI(lifespan=lifespan)

# 设置允许前端跨域连接
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # 允许所有的源
    allow_credentials=True,
    allow_methods=["*"],    # 允许所有的HTTP方法
    allow_headers=["*"],    # 允许所有的HTTP头
)

# 设置日志
logger.remove()
logger.add("main.log", rotation="1 GB", backtrace=True, diagnose=True, format="{time} {level} {message}")

# 根目录访问的处理
@app.get("/")
async def read_root():
    return json.dumps({"code": 0, "msg": "欢迎访问", "data": ""})

@app.post("/store_content")
async def store_content(request: StoreContent):
    """存储聊天信息，每次存储一条，user/assistant。
    """
    # 插入聊天记录到chat_history表
    execute_status = await insert_chat_history(request.user_id, request.session_id, request.role, request.content)
    if execute_status:
        return json.dumps({"code": 0, "msg": "信息存储成功", "data": {"status": True}})
    else:
        return json.dumps({"code": 0, "msg": "信息存储失败", "data":  {"status": False}})

@app.post("/get_chat_history")
async def get_chat_history(request: FetchChatHistory):
    """根据user_id和session_id获取用户的所有聊天记录。
    Returns:
        chat_history(list(dict)):根据user_id和session_id获取用户的所有聊天记录，通过录入时间排序。
    """
    # 获取全部的聊天记录
    chat_history = await fetch_chat_history(request.user_id, request.session_id)
    # 如果有聊天记录
    if chat_history:
        return json.dumps({"code": 0, "msg": "获取用户聊天记录成功", "data":  {"chat_history": chat_history}})
    # 如果聊天记录为空
    else:
        logger.error(f"聊天记录为空")
        return json.dumps({"code": 0, "msg": "获取用户聊天记录成功", "data":  {"chat_history": []}})


if __name__ == "__main__":
    import uvicorn
    try:
        uvicorn.run(app, host="0.0.0.0", port=8847)
    except Exception as e:
        logger.error(f"启动服务器时出错: {e}")