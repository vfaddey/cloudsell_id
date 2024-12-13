from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from src.core.config import settings

engine = create_async_engine(
    url=settings.DB_URL)
AsyncSessionFactory = async_sessionmaker(bind=engine,
                                         expire_on_commit=False,
                                         class_=AsyncSession)
Base = declarative_base()