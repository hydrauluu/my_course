from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        from sqlalchemy import inspect, text
        def _migrate(sync_conn):
            inspector = inspect(sync_conn)
            columns = [c["name"] for c in inspector.get_columns("lectures")]
            if "content" not in columns:
                sync_conn.execute(text("ALTER TABLE lectures ADD COLUMN content TEXT"))
        await conn.run_sync(_migrate)
