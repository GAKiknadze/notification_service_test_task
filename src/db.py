from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .logger import logger
from .models import Base

engine: AsyncEngine


@logger.catch
async def init_db(uri: str, create_models: bool = False) -> None:
    """Инициализация AsyncEngine"""
    global engine

    engine = create_async_engine(uri, future=True)

    if create_models:
        """Создание таблиц в базе данных"""
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Получение сессии базы данных"""
    global engine  # noqa: F824
    local_session = async_sessionmaker(
        engine,
        autocommit=False,
        autoflush=True,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    async with local_session() as session:
        yield session
