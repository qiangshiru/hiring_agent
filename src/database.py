from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import Settings, get_settings

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


def create_engine(settings: Settings) -> AsyncEngine:
    connect_args: dict[str, object] = {}
    if settings.database_url.startswith("sqlite+aiosqlite"):
        connect_args["check_same_thread"] = False

    engine_kwargs: dict[str, object] = {
        "echo": settings.database_echo,
        "connect_args": connect_args,
    }
    if not settings.database_url.startswith("sqlite+aiosqlite"):
        engine_kwargs["pool_size"] = settings.database_pool_size
        engine_kwargs["max_overflow"] = settings.database_max_overflow

    return create_async_engine(
        settings.database_url,
        **engine_kwargs,
    )


@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    return create_engine(get_settings())


@lru_cache(maxsize=1)
def get_session_maker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(get_engine(), expire_on_commit=False, class_=AsyncSession)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async_session_local = get_session_maker()
    async with async_session_local() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
