from typing import Any, Dict, List

from sqlalchemy import literal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select

from .model.stamps import Stamps as StampsModel


class Stamps(object):
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
