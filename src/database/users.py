from typing import Any, Dict, Union

from sqlalchemy import select, literal
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from .model.users import Users as UsersModel


class Users(object):
    @staticmethod
    async def exists_by_email(session: AsyncSession, email: str) -> bool:
        return (
            await session.execute(
                select(
                    literal(True),
                ).where(
                    select(
                        UsersModel.email,
                    ).where(
                        UsersModel.email == email,
                    ).exists(),
                )
            )
        ).scalar() is True

    @staticmethod
    async def by_id(session: AsyncSession, user_id: int) -> Union[None, Dict[str, Any]]:
        result: Union[None, Row] = (
            await session.execute(
                select(
                    [
                        UsersModel.first_name,
                        UsersModel.last_name,
                        UsersModel.email,
                        UsersModel.profile_picture,
                    ],
                ).where(
                    UsersModel.id == user_id,
                ),
            )
        ).first()

        return None if result is None else result._asdict()
