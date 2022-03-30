from typing import Any, Dict, List, Union, Optional

from sqlalchemy import literal
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select, Select

from .model.employees import Employees as EmployeesModel
from .model.users import Users as UsersModel
from ..exceptions import DatabaseError


class Employees(object):
    @staticmethod
    async def exists(session: AsyncSession, user_id: int) -> bool:
        """
        Method for determining if an employee exists in the database

        params:
            session : AsyncSession -> connection to the database
            user_id : int -> id of the employee
        returns:
            bool : employee is or is not in DB
        throws:
            ValueError: user_id not int
        """
        try:
            return (
                await session.execute(
                    select(
                        [literal(True), ],
                    ).where(
                        select(
                            [EmployeesModel, ],
                        ).where(
                            EmployeesModel.id == user_id,
                        ).exists(),
                    )
                )
            ).scalar() is True
        except Exception as ex:
            raise DatabaseError(ex)

    @staticmethod
    def __query() -> Select:
        return select(
            [
                UsersModel.first_name,
                UsersModel.last_name,
                UsersModel.email,
                UsersModel.profile_picture,
                EmployeesModel.added_by,
                EmployeesModel.can_reward,
                EmployeesModel.place_id
            ],
            from_obj=EmployeesModel,
        ).join(
            UsersModel,
            EmployeesModel.id == UsersModel.id,
        )

    @staticmethod
    async def by_id(session: AsyncSession, employee_id: int) -> Optional[Dict[str, Any]]:
        try:
            result: Union[None, Row] = (
                await session.execute(
                    Employees.__query().where(
                        EmployeesModel.id == employee_id,
                    ),
                )
            ).first()
        except Exception as ex:
            raise DatabaseError(ex)

        return None if result is None else result._asdict()

    @staticmethod
    async def all_by_place(session: AsyncSession, place_id: int) -> List[Dict[str, Any]]:
        try:
            return list(
                map(
                    lambda result: result._asdict(),
                    await (
                        await session.stream(
                            Employees.__query().where(
                                EmployeesModel.place_id == place_id,
                            ),
                        )
                    ).all(),
                ),
            )
        except Exception as ex:
            raise DatabaseError(ex)
