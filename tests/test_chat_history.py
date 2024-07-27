"""
Description: 测试聊天信息存储、获取接口。
Notes: 
1. 测试 `/store_content` 接口时，一定记得先传 user 信息，再传 assistant 信息，两者交替！！！
2. 笔者接口返回的格式为json，不能使用 `response.text()` 获取内容。`response.text()` 返回的是一个字符串，需要将 `result = await response.text()`改
为 `result = await response.json()`。 然后进行 `json.loads()`可以正确将数据解析，类型为`dict`(数据为中文)。
"""
import aiohttp
import asyncio
import json

async def test_store_content(session, url, data):
    async with session.post(url, json=data) as response:
        assert response.status == 200
        result = await response.json()
        result = json.loads(result)
        print(result, type(result))

async def test_get_chat_history(session, url, data):
    async with session.post(url, json=data) as response:
        assert response.status == 200
        result = await response.json()
        result = json.loads(result)
        print(result, type(result))

async def main():
    async with aiohttp.ClientSession() as session:
        base_url = "http://localhost:8847"

        # 测试 /store_content 接口
        store_content_url = f"{base_url}/store_content"
        store_content_data = {
            "user_id": 1,   # 固定不变
            "session_id": "86d8734a-0029-4d95-a80c-f50ad6f8a61b",   # 固定不变
            # "role": "assistant",    # 用户的消息使用 "user"，客服的消息使用 "assistant"。
            # "content": "北京是..."  # 当前信息
            "role": "user",    # 用户的消息使用 "user"，客服的消息使用 "assistant"。
            "content": "请介绍一下北京"  # 当前信息
        }
        await test_store_content(session, store_content_url, store_content_data)

        # 测试 /get_chat_history 接口（当前接口会一次性获取指定用户的所有聊天信息，奇数索引为用户消息，偶数索引为客服消息）
        get_chat_history_url = f"{base_url}/get_chat_history"
        get_chat_history_data = {
            "user_id": 1,   # 固定不变
            "session_id": "86d8734a-0029-4d95-a80c-f50ad6f8a61b"    # 固定不变
        }
        await test_get_chat_history(session, get_chat_history_url, get_chat_history_data)

if __name__ == "__main__":
    asyncio.run(main())