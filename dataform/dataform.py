from pydantic import BaseModel, Field

class FetchChatHistory(BaseModel):
    """获取用户历史的表单"""
    user_id: int = Field(..., title="用户id")
    session_id: str = Field(default='86d8734a-0029-4d95-a80c-f50ad6f8a61b', title="会话id")