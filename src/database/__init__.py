from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from ..utils.enviromental_variables import USER, PASS, HOST, DATABASE
from .model import *


database: AsyncEngine


async def db_init():
    global database

    database = create_async_engine(
        f'postgresql+asyncpg://{USER}:{PASS}@{HOST}/{DATABASE}')

    async with database.begin() as connection:
        await connection.run_sync(ORMBase.metadata.create_all,)
