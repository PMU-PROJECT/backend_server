from typing import Union, Tuple

from sqlalchemy.sql.expression import insert, select, literal, asc, literal_column
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from .model.local_users import LocalUsers as LocalUsersModel
from .model.users import Users as UsersModel
from .users import Users
from ..exceptions import DatabaseError


class LocalUsers:
    @staticmethod
    async def by_email(session: AsyncSession, email: str) -> Tuple[Union[None, int], bytes]:
        try:
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
        except Exception as ex:
            raise DatabaseError(ex)

        return result[1], result[2]

    @staticmethod
    async def insert(session: AsyncSession, first_name: str, last_name: str, email: str, password_hash: bytes) -> int:
        user_id = await Users.insert(session, first_name, last_name, email)

        try:
            # Store the password hash
            await session.execute(
                insert(
                    LocalUsersModel,
                ).values(
                    user_id=user_id,
                    pw_hash=password_hash,
                ),
            )

            await session.flush()
        except Exception as ex:
            raise DatabaseError(ex)

        return user_id
