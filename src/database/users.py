from typing import Any, Dict, Union

from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import insert, select, literal
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from .model.users import Users as UsersModel
from ..config.logger_config import logger
from ..exceptions import BadUserRequest, DatabaseError


class Users(object):
    @staticmethod
    async def exists_by_email(session: AsyncSession, email: str) -> bool:
        try:
            return (
                await session.execute(
                    select(
                        [literal(True), ],
                    ).where(
                        select(
                            UsersModel.email,
                        ).where(
                            UsersModel.email == email,
                        ).exists(),
                    )
                )
            ).scalar() is True
        except Exception as ex:
            raise DatabaseError(ex)

    @staticmethod
    async def by_id(session: AsyncSession, user_id: int) -> Union[None, Dict[str, Any]]:
        try:
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
        except Exception as ex:
            raise DatabaseError(ex)

        return None if result is None else {
            col: getattr(result, col)
            for col in result.keys()
        }

    @staticmethod
    async def insert(session: AsyncSession, first_name: str, last_name: str, email: str) -> int:
        if await Users.exists_by_email(session, email):
            logger.debug("Email already exists")

            raise BadUserRequest("User with this email already exists!")

        # Only email has strict syntax. If syntax not valid, raise exception
        try:
            user_id: int = (
                await session.execute(
                    insert(
                        UsersModel,
                    ).values(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                    ).returning(
                        UsersModel.id,
                    ),
                )
            ).scalar()

            await session.flush()

            return user_id
        except IntegrityError:
            raise BadUserRequest("Email not valid")
        except Exception as ex:
            raise DatabaseError(ex)
