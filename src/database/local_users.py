from typing import Union, Tuple

from postgresql.types import Row
from sqlalchemy import select, literal
from sqlalchemy.ext.asyncio import AsyncSession

from .model.local_users import LocalUsers as LocalUsersModel
from .model.users import Users as UsersModel


class LocalUsers:
    @staticmethod
    async def by_email(session: AsyncSession, email: str) -> Tuple[Union[None, int], bytes]:
        result: Row = (
            await session.execute(
                select(
                    [
                        UsersModel.id,
                        LocalUsersModel.pw_hash,
                    ],
                ).join(
                    UsersModel,
                    LocalUsersModel.id == UsersModel.id,
                ).where(
                    UsersModel.email == email,
                ).union(
                    select(
                        [
                            literal(None, ),
                            literal(b'', ),
                        ],
                    ),
                ).limit(1),
            )
        ).one()

        return result[0], result[1]
