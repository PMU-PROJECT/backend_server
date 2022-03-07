from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select, literal

from .model.images import Images as ImagesModel


class Images(object):
    @staticmethod
    async def all_by_place(session: AsyncSession, place_id: int) -> List[str]:
        return await (
            await session.stream_scalars(
                select(
                    [
                        ImagesModel.filename,
                    ],
                ).where(
                    ImagesModel.place_id == literal(place_id, ),
                ),
            )
        ).all()
