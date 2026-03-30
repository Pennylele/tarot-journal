from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
import os
from dotenv import load_dotenv

# This looks for the .env file and loads it into os.environ
load_dotenv()

# Use an environment variable, fallback to the dev string only if necessary
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
)

if SQLALCHEMY_DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set in the environment or .env file!")


# This is for PostgreSQL
# "echo=True" only for dev env
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Registry for database
class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
