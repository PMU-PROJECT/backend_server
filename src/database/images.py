from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import literal, select

from .model.images import Images as ImagesModel
from ..exceptions import DatabaseError


class Images(object):
    @staticmethod
    async def first_by_place(session: AsyncSession, place_id: int) -> Optional[str]:
        try:
            return (await session.execute(
                select(
                    [ImagesModel.filename, ], ).where(
                    ImagesModel.place_id == literal(place_id), ), )).scalar()
        except Exception as ex:
            raise DatabaseError(ex)

    @staticmethod
    async def all_by_place(session: AsyncSession, place_id: int) -> List[str]:
        try:
            return (await session.execute(
                select(
                    [ImagesModel.filename, ], ).where(
                    ImagesModel.place_id == literal(place_id, ), ), )).scalars().all()
        except Exception as ex:
            raise DatabaseError(ex)
