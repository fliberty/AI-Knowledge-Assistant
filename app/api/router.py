"""
API 路由聚合

汇总所有版本的 API 路由到统一的 router。
"""

from fastapi import APIRouter

from app.api.v1.endpoints import chat, health, knowledge, session

api_router = APIRouter()

# 无版本前缀的端点
api_router.include_router(health.router)

# v1 版本端点
api_router.include_router(chat.router, prefix="/api/v1")
api_router.include_router(knowledge.router, prefix="/api/v1")
api_router.include_router(session.router, prefix="/api/v1")
