from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from sqlalchemy.ext.declarative import declarative_base

db_url=settings.database_url
engine=create_engine(url=db_url)

session_Local=sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base=declarative_base()




