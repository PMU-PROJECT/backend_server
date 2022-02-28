from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select, literal

from .model.images import Images as ImagesModel
from .model.places import Places as PlacesModel


class Images(object):
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
