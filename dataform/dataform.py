from pydantic import BaseModel, Field

class StoreContent(BaseModel):
    """存储用户当前输入的表单"""
    user_id: int = Field(..., title="用户id")
    session_id: str = Field(default='86d8734a-0029-4d95-a80c-f50ad6f8a61b', title="会话id")
    role: str = Field(..., title="会话id")
    content: str = Field(..., title="用户当前输入")

class FetchChatHistory(BaseModel):
    """获取用户历史的表单"""
    user_id: int = Field(..., title="用户id")
    session_id: str = Field(default='86d8734a-0029-4d95-a80c-f50ad6f8a61b', title="会话id")