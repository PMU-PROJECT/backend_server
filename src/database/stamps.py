from typing import Any, Dict, List

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select, insert

from .model.stamps import Stamps as StampsModel


class Stamps(object):
    @staticmethod
    async def add_stamp(session: AsyncSession, visitor_id: int, employee_id: int, place_id: int) -> bool:
        try:
            await session.execute(
                insert(
                    StampsModel,
                ).values(
                    visitor_id=visitor_id,
                    place_id=place_id,
                    employee_id=employee_id,
                ),
            )
        except IntegrityError:
            return False

        return True

    @staticmethod
    async def add_stamp(session: AsyncSession, stamp: StampsModel) -> bool:
        try:
            await session.execute(
                insert(
                    StampsModel,
                ).values(
                    visitor_id=stamp.visitor_id,
                    place_id=stamp.place_id,
                    employee_id=stamp.employee_id,
                ),
            )
        except IntegrityError:
            return False

        return True

    @staticmethod
    async def all(session: AsyncSession, visitor_id: int) -> List[Dict[str, Any]]:
        return list(
            map(
                lambda result: result._asdict(),
                await (
                    await session.stream(
                        select(
                            [
                                StampsModel.visitor_id,
                                StampsModel.place_id,
                                StampsModel.employee_id,
                                StampsModel.given_on,
                            ],
                        ).where(
                            StampsModel.visitor_id == visitor_id,
                        ),
                    )
                ).all(),
            ),
        )
