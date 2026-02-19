from typing import TYPE_CHECKING, Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import URL, text

from app.store.database import BaseModel

if TYPE_CHECKING:
    from app.web.app import Application


class Database:
    def __init__(self, app: "Application") -> None:
        self.app = app

        self.engine: AsyncEngine | None = None
        self._db: type[DeclarativeBase] = BaseModel
        self.session: async_sessionmaker[AsyncSession] | None = None

    async def connect(self, *args: Any, **kwargs: Any) -> None:
        self.engine = create_async_engine(
            URL.create(
                drivername="postgresql+asyncpg",
                username=self.app.config.database.user,
                password=self.app.config.database.password,
                host=self.app.config.database.host,
                port=self.app.config.database.port,
                database=self.app.config.database.database,
            )
        )
        self.session = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def disconnect(self, *args: Any, **kwargs: Any) -> None:
        if self.engine:
            await self.engine.dispose()
    
    async def clear(self) -> None:
        """Clear all tables for testing purposes"""
        if not self.engine:
            return
            
        async with self.engine.begin() as conn:
            await conn.execute(text("TRUNCATE TABLE answers CASCADE"))
            await conn.execute(text("TRUNCATE TABLE questions CASCADE"))
            await conn.execute(text("TRUNCATE TABLE themes CASCADE"))
            await conn.execute(text("TRUNCATE TABLE admins CASCADE"))
            
            # Reset sequences
            await conn.execute(text("ALTER SEQUENCE answers_id_seq RESTART WITH 1"))
            await conn.execute(text("ALTER SEQUENCE questions_id_seq RESTART WITH 1"))
            await conn.execute(text("ALTER SEQUENCE themes_id_seq RESTART WITH 1"))
            await conn.execute(text("ALTER SEQUENCE admins_id_seq RESTART WITH 1"))
