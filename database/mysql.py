"""
Description: 定义MySQL数据库的连接与断连。
Notes: 
1. 数据库定义文件只定义连接和断连，然后在该文件实例化，其他涉及数据库操作的函数都只从mysql连接池获取一条连接。
"""
import os
import aiomysql
from loguru import logger

class MySQLER:
    def __init__(self):
        # 从环境变量获取数据库配置
        self.mysql_host = os.getenv("MYSQL_DB_HOST")
        self.mysql_dbname = os.getenv("MYSQL_DB_NAME")
        self.mysql_user = os.getenv("MYSQL_DB_USER")
        self.mysql_password = os.getenv("MYSQL_DB_PASSWORD")
        self.mysql_port = int(os.getenv("MYSQL_DB_PORT"))

        self.pool = None

    async def create_connect_pool(self):
        try:
            # 尝试连接数据库
            self.pool = await aiomysql.create_pool(
                host=self.mysql_host,
                port=self.mysql_port,
                user=self.mysql_user,
                password=self.mysql_password,
                db=self.mysql_dbname,
                cursorclass=aiomysql.DictCursor,
                autocommit=True
            )
        except aiomysql.Error as error:
            logger.info(f"创建mysql连接池时出错,错误信息为: {error}")

    async def disconnect(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

mysqler = MySQLER()

def get_mysql_connect_pool():
    # 从mysql连接池中获取一条连接。
    return mysqler.pool
