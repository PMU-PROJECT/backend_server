from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select

from .model.reward_types import RewardTypes as RewardTypesModel
from ..exceptions import DatabaseError


class RewardTypes(object):
    @staticmethod
    async def all(session: AsyncSession) -> List[Dict[str, Any]]:
        try:
            return list(
                map(
                    lambda result: result._asdict(), (
                        await session.execute(
                            select(
                                [RewardTypesModel, ],
                            ),
                        )
                    ).all(),
                ),
            )
        except Exception as ex:
            raise DatabaseError(ex)
