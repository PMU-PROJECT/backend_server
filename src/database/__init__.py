from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .model import *
from ..utils.enviromental_variables import USER, PASS, HOST, DATABASE

database: AsyncEngine = create_async_engine(
    f'postgresql+asyncpg://{USER}:{PASS}@{HOST}/{DATABASE}')

async_session: sessionmaker = sessionmaker(
    bind=database,
    class_=AsyncSession,
    autocommit=True,
)


async def db_init():
    global database

    async with database.begin() as connection:
        await connection.run_sync(ORMBase.metadata.create_all, )
