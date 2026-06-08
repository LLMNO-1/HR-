"""
API 接口共用的通用 Schema 模型
"""
from pydantic import BaseModel


class TaskResponse(BaseModel):
    """异步任务创建后的通用响应"""
    task_id: int
    status: str = "processing"
    message: str = "任务已提交，请轮询查询结果"


class ErrorResponse(BaseModel):
    """错误响应"""
    detail: str
