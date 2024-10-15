from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import AsyncGenerator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql+asyncpg://postgres:python$_venv@localhost:5432/CommetBase"

CommentBase = declarative_base()

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,  
)

async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False  
)

async def get_comment_service_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            logger.info("Creating new database session")
            yield session
        except Exception as e:
            logger.error(f"An error occurred during the session: {e}")
            raise  
        finally:
            logger.info("Closing database session")
            await session.close()

