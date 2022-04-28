from sqlalchemy import select, literal
from sqlalchemy.ext.asyncio import AsyncSession

from .model.administrators import Administrators as AdministratorsModel
from ..exceptions import DatabaseError


class Administrators(object):
    @staticmethod
    async def exists(session: AsyncSession, user_id: int) -> bool:
        try:
            return (
                await session.execute(
                    select(
                        [literal(True), ],
                    ).where(
                        select(
                            [AdministratorsModel, ],
                        ).where(
                            AdministratorsModel.user_id == user_id,
                        ).exists(),
                    )
                )
            ).scalar() is True
        except Exception as ex:
            raise DatabaseError(ex)
