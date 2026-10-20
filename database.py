from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from config import settings

engine = create_async_engine(url=settings.database_url, pool_pre_ping=True)

session_Local = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
Base = declarative_base()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)