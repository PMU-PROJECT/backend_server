from typing import Any, Dict, List

from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.functions import count

from .model.reward_types import RewardTypes as RewardTypesModel
from .model.rewards_log import RewardsLog as RewardsLogModel
from .model.stamps import Stamps as StampsModel
from ..exceptions import BadUserRequest, DatabaseError


class RewardTypes(object):
    @staticmethod
    async def all(session: AsyncSession) -> List[Dict[str, Any]]:
        try:
            return list(
                map(
                    lambda result: result._asdict(), (
                        await session.execute(
                            select(
                                RewardTypesModel.id,
                                RewardTypesModel.name,
                                RewardTypesModel.description,
                                RewardTypesModel.minimum_stamps,
                            ),
                        )
                    ).all(),
                ),
            )
        except Exception as ex:
            raise DatabaseError(ex)

    @staticmethod
    async def eligible(session: AsyncSession, visitor_id: int) -> List[Dict[str, Any]]:
        try:
            return list(
                map(
                    lambda result: result._asdict(), (
                        await session.execute(
                            select(
                                [RewardTypesModel, ],
                            ).where(
                                RewardTypesModel.id.notin_(
                                    select(
                                        [RewardsLogModel.reward_id, ],
                                    ).where(
                                        RewardsLogModel.visitor_id == visitor_id,
                                    ).subquery(),
                                ),
                                RewardTypesModel.minimum_stamps <= select(
                                    [count(), ],
                                ).where(
                                    StampsModel.visitor_id == visitor_id,
                                ).scalar_subquery(),
                            ),
                        )
                    ).all(),
                ),
            )
        except Exception as ex:
            raise DatabaseError(ex)

    @ staticmethod
    async def minimum_stamps(session: AsyncSession, reward_id: int) -> int:
        try:
            return (
                await session.execute(
                    select(
                        [RewardTypesModel.minimum_stamps, ],
                    ).where(
                        RewardTypesModel.id == reward_id,
                    ).limit(
                        1,
                    ),
                )
            ).scalar_one()
        except NoResultFound:
            raise BadUserRequest("No such reward exists!")
        except Exception as ex:
            raise DatabaseError(ex)
