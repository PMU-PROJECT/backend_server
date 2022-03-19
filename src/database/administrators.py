from sqlalchemy import select, literal
from sqlalchemy.ext.asyncio import AsyncSession

from .model.administrators import Administrators as AdministratorsModel


class Administrators(object):
    @staticmethod
    async def exists(session: AsyncSession, user_id: int) -> bool:
        return bool(
            (
                await session.execute(
                    select(
                        [literal(True), ],
                    ).where(
                        select(
                            [AdministratorsModel, ],
                        ).where(
                            AdministratorsModel.id == user_id,
                        ).exists(),
                    )
                )
            ).scalar()
        )
