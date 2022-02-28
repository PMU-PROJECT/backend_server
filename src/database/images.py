from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select, literal

from .model.images import Images as ImagesModel


class Images(object):
    @staticmethod
    async def all_by_place(session: AsyncSession, id: int) -> List[str]:
        return (
            await session.stream(
                select(
                    [
                        ImagesModel.data,
                    ],
                ).where(
                    ImagesModel.place_id == literal(id,),
                ),
            )
        ).scalars().all()
