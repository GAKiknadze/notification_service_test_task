from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .logger import logger

AsyncSessionLocal: sessionmaker[AsyncSession]  # type:ignore[type-var]


@logger.catch
def init_db(uri: str, **kwargs) -> None:
    global AsyncSessionLocal

    async_engine = create_async_engine(uri, echo=True, future=True)

    AsyncSessionLocal = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
        **kwargs
    )  # type:ignore[call-overload]


@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession]:
    global AsyncSessionLocal  # noqa: F824
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as exc:
            await session.rollback()
            raise exc
        finally:
            await session.close()
