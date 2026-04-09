"""
FastAPI 依赖注入

提供 Settings、QdrantService 等全局依赖的注入点。
"""

from typing import Annotated

from fastapi import Depends, HTTPException, Request

from app.core.config import Settings, get_settings
from app.services.vector_store import QdrantService


def get_qdrant_service(request: Request) -> QdrantService:
    """从应用 state 中获取 QdrantService 单例。"""
    service = getattr(request.app.state, "qdrant_service", None)
    if service is None:
        raise HTTPException(
            status_code=503,
            detail="知识库服务不可用，请确保 Qdrant 向量数据库已启动",
        )
    return service


# 类型别名，简化端点函数签名
SettingsDep = Annotated[Settings, Depends(get_settings)]
QdrantDep = Annotated[QdrantService, Depends(get_qdrant_service)]

