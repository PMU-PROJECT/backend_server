from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import insert, select, update

from .model.google_user import GoogleUsers as GoogleUsersModel
from .model.users import Users as UsersModel
from ..exceptions import DatabaseError


class GoogleUsers:
    @staticmethod
    async def user_id_by_google_id(session: AsyncSession, google_id: str) -> Optional[int]:
        try:
            return (
                await session.execute(
                    select(
                        [UsersModel.user_id, ],
                    ).select_from(
                        UsersModel,
                    ).join(
                        GoogleUsersModel,
                        GoogleUsersModel.user_id == UsersModel.user_id,
                    ).where(
                        GoogleUsersModel.google_id == google_id,
                    ),
                )
            ).scalar()
        except Exception as ex:
            raise DatabaseError(ex)

    @staticmethod
    async def insert_or_replace(
            session: AsyncSession,
            google_id: str,
            first_name: str,
            last_name: str,
            email: str,
    ) -> int:
        user_id: Optional[int] = await GoogleUsers.user_id_by_google_id(session, google_id)

        try:
            if user_id is None:
                del user_id

                user_id: int = (
                    await session.execute(
                        insert(
                            UsersModel,
                        ).values(
                            first_name=first_name,
                            last_name=last_name,
                            email=email,
                        ).returning(
                            UsersModel.user_id,
                        ),
                    )
                ).scalar_one()

                await session.flush()

                await session.execute(
                    insert(
                        GoogleUsersModel,
                    ).values(
                        user_id=user_id,
                        google_id=google_id,
                    ),
                )
            else:
                await session.execute(
                    update(
                        UsersModel,
                    ).values(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                    ).where(
                        UsersModel.user_id == user_id,
                    )
                )

            await session.flush()

            return user_id
        except Exception as ex:
            raise DatabaseError(ex)
