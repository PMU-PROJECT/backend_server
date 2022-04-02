from typing import Any, Dict, List

from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select, and_

from .model.reward_types import RewardTypes as RewardTypesModel
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
    async def eligible(session: AsyncSession, stamp_count: int, reward_id_blocklist: list) -> List[Dict[str, Any]]:
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
                                RewardTypesModel.picture,
                            ).where(
                                RewardTypesModel.id.notin_(
                                    reward_id_blocklist),
                                RewardTypesModel.minimum_stamps <= stamp_count
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
