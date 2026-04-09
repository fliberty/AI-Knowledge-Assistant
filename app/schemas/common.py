"""
通用响应模型

提供统一的 API 响应格式包装。
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """错误详情。"""

    code: str = Field(..., description="错误代码", examples=["VALIDATION_ERROR"])
    message: str = Field(..., description="错误描述")
    details: dict[str, Any] | None = Field(default=None, description="附加详情")


class APIResponse(BaseModel, Generic[T]):
    """统一 API 响应包装器。"""

    success: bool = Field(default=True, description="请求是否成功")
    data: T | None = Field(default=None, description="响应数据")
    error: ErrorDetail | None = Field(default=None, description="错误信息")
    message: str = Field(default="OK", description="响应消息")
