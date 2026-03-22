from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

SQLALCHEMY_DATABSE_URL = "sqlite_aiosqlite:///./tarot.db"

# This is for sqlite
engine = create_async_engine(
    SQLALCHEMY_DATABSE_URL, connect_args={"check_same_thread": False}
)

AyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AyncSessionLocal() as session:
        yield session
