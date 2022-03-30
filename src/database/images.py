from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import literal, select

from .model.images import Images as ImagesModel


class Images(object):
    @staticmethod
    async def first_by_place(session: AsyncSession, place_id: int) -> Optional[str]:
        return (await session.execute(
            select(
                [ImagesModel.filename, ], ).where(
                ImagesModel.place_id == literal(place_id), ), )).scalar()

    @staticmethod
    async def all_by_place(session: AsyncSession, place_id: int) -> List[str]:
        return (await session.execute(
            select(
                [ImagesModel.filename, ], ).where(
                ImagesModel.place_id == literal(place_id, ), ), )).scalars().all()
