from typing import Any, Dict, Union

from sqlalchemy import select
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from .model.users import Users as UsersModel


class Users(object):
    @staticmethod
    async def by_id(session: AsyncSession, user_id: int) -> Union[None, Dict[str, Any]]:
        result: Union[None, Row] = (
            await session.stream(
                select(
                    [
                        UsersModel.first_name,
                        UsersModel.last_name,
                        UsersModel.email,
                        UsersModel.profile_picture,
                    ],
                ).where(
                    UsersModel.id == user_id
                ),
            )
        ).scalar()

        return None if result is None else result._asdict()
