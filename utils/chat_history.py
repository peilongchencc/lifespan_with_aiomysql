from loguru import logger
from database.mysql import get_mysql_connect_pool

async def insert_chat_history(user_id: int, conversation_id: str, role: str, content: str):
    """插入聊天记录到chat_history表
    Returns:
        True: 插入成功。
        False: 插入失败。
    """
    sql_query = """
    INSERT INTO chat_history (user_id, conversation_id, role, content)
    VALUES (%s, %s, %s, %s)
    """
    # 从mysql连接池中获取一条连接。
    mysqler_pool = get_mysql_connect_pool()
    async with mysqler_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                await cursor.execute(sql_query, (user_id, conversation_id, role, content))
                await conn.commit()
                return True
            except Exception as error:
                await conn.rollback()
                logger.info(f"插入聊天记录时出错,错误信息为: {error}")
                return False


async def fetch_chat_history(user_id: int, conversation_id: str):
    """插入聊天记录到chat_history表
    Notes:
        SQL排序默认是升序的，对于时间字段，表示从最早的时间到最近的时间排序。
    """
    sql_query = """
    SELECT role, content FROM chat_history
    WHERE user_id = %s AND conversation_id = %s
    ORDER BY entry_time;
    """
    # 从mysql连接池中获取一条连接。
    mysqler_pool = get_mysql_connect_pool()
    async with mysqler_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                await cursor.execute(sql_query, (user_id, conversation_id))
                results = await cursor.fetchall()
                return results
            except Exception as error:
                logger.info(f"从MySQL获取chat_history时出错,错误信息为: {error}")
                return None