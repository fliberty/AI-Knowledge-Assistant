"""
AI Knowledge Assistant — FastAPI 应用入口

生命周期管理：
    - startup: 初始化日志系统、Qdrant 连接
    - shutdown: 关闭 Qdrant 连接
"""

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.services.vector_store import QdrantService
from app.db.session import init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """应用生命周期管理。"""
    # ── Startup ──────────────────────────────
    setup_logging()
    settings = get_settings()
    logger.info("[STARTUP] 正在启动 %s v%s", settings.app_name, settings.app_version)

    # 初始化数据库建表
    try:
        await init_db()
        logger.info("[OK] 数据库表结构同步完成")
    except Exception as e:
        logger.error("[FAIL] 数据库初始化失败: %s", e)

    qdrant_service = None
    try:
        # 初始化 Qdrant 服务
        qdrant_service = QdrantService(settings)
        await qdrant_service.initialize()
        app.state.qdrant_service = qdrant_service
        logger.info("[OK] 应用启动完成")
    except Exception as e:
        logger.error("[FAIL] Qdrant 初始化失败 (应用仍将启动，但知识库功能不可用): %s", e, exc_info=True)
        app.state.qdrant_service = None

    yield

    # ── Shutdown ─────────────────────────────
    logger.info("[SHUTDOWN] 正在关闭应用...")
    if qdrant_service:
        await qdrant_service.close()
    logger.info("[DONE] 应用已关闭")


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用实例。"""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="企业级 AI 知识库助手 — 基于 LangGraph + RAG 架构",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS 中间件 ──────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境应限制为具体域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── 挂载路由 ─────────────────────────────
    app.include_router(api_router)

    return app


# 应用实例（uvicorn 入口）
app = create_app()
