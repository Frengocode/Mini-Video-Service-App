from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

VIDEO_SERVICE_DATABASE_URL = 'postgresql+asyncpg://postgres:python$_venv@localhost:5432/VideoService'

Base = declarative_base()

engine = create_async_engine(VIDEO_SERVICE_DATABASE_URL)

async_session_maker = sessionmaker(bind = engine, class_ = AsyncSession)


async def get_video_service_session() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()