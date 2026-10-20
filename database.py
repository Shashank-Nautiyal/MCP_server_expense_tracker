from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from config import settings
from sqlalchemy.ext.declarative import declarative_base

db_url=settings.database_url
engine=create_async_engine(url=db_url,pool_per_ping=True)

session_Local=async_sessionmaker(engine,expire_on_commit=False, autoflush=False)
Base=declarative_base()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



