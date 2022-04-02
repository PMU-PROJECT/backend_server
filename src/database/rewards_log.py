from typing import Any, Dict, List

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select, insert

from .model.rewards_log import RewardsLog as RewardsLogModel
from .reward_types import RewardTypes
from .stamps import Stamps
from ..exceptions import BadUserRequest, DatabaseError


class RewardsLog(object):
    @staticmethod
    async def all_by_visitor_id(session: AsyncSession, visitor_id: int) -> List[Dict[str, Any]]:
        try:
            return list(
                map(
                    lambda result: result._asdict(), (
                        await session.execute(
                            select(
                                RewardsLogModel.employee_id,
                                RewardsLogModel.visitor_id,
                                RewardsLogModel.reward_id,
                                RewardsLogModel.given_on,
                            ).where(
                                RewardsLogModel.visitor_id == visitor_id,
                            ),
                        )
                    ).all(),
                ),
            )
        except Exception as ex:
            raise DatabaseError(ex)

    @staticmethod
    async def insert(session: AsyncSession, visitor_id: int, reward_id: int, employee_id: int) -> bool:
        if await Stamps.stamp_count(session, visitor_id) < await RewardTypes.minimum_stamps(session, reward_id):
            raise BadUserRequest("User doesn't have enough stamps!")

        try:
            await session.execute(
                insert(
                    RewardsLogModel,
                ).values(
                    visitor_id=visitor_id,
                    reward_id=reward_id,
                    employee_id=employee_id,
                )
            )
        except IntegrityError:
            return False
        except Exception as ex:
            raise DatabaseError(ex)

        return True
