from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from app.core.config import get_settings
import os

settings = get_settings()

db_url = settings.database_url
is_sqlite = db_url.startswith("sqlite")

# 如果是 SQLite，确保目录存在
if is_sqlite:
    db_path = db_url.split("///")[-1]
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

engine = create_async_engine(
    db_url,
    echo=False,  # Set to True for SQL query logging
    future=True
)

async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def init_db():
    """在应用启动时构建数据库表结构。"""
    from app.models.chat_session import ChatSession, ChatMessage
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_db() -> AsyncSession:
    """提供供 FastAPI Depend 使用的数据连接。"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
