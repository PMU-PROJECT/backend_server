from typing import Union, Tuple

from sqlalchemy import select, literal, asc, literal_column
from sqlalchemy.engine import Row
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
                        literal(
                            0,
                        ).label(
                            'record',
                        ),
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
                            literal(
                                1,
                            ),
                            literal(
                                None,
                            ),
                            literal(
                                b'',
                            ),
                        ],
                    ),
                ).limit(
                    1,
                ).order_by(
                    asc(
                        literal_column(
                            'record',
                        ),
                    ),
                ),
            )
        ).one()

        return result[1], result[2]
