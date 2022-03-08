from typing import Any, Dict, List, Union

from sqlalchemy import literal
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Join
from sqlalchemy.sql.expression import select

from .model.employees import Employees as EmployeesModel
from .model.users import Users as UsersModel


class Employees(object):
    @staticmethod
    async def exists(session: AsyncSession, user_id: int) -> bool:
        return bool(
            (
                await session.execute(
                    select(literal(True))
                        .where(
                        select(EmployeesModel)
                            .where(
                            EmployeesModel.id == user_id,
                        )
                            .exists(),
                    )
                )
            ).scalar()
        )

    @staticmethod
    def __query() -> Join:
        return select(
            [
                UsersModel.first_name,
                UsersModel.last_name,
                UsersModel.email,
                UsersModel.profile_picture,
                EmployeesModel.added_by,
                EmployeesModel.can_reward,
            ],
            from_obj=EmployeesModel,
        ).join(
            UsersModel,
            EmployeesModel.id == UsersModel.id,
        )

    @staticmethod
    async def by_id(session: AsyncSession, employee_id: int) -> Union[None, Dict[str, Any]]:
        result: Union[None, Row] = (
            await session.execute(
                Employees.__query()
                .where(
                    EmployeesModel.id == employee_id
                ),
            )
        ).first()

        return None if result is None else result._asdict()

    @staticmethod
    async def all_by_place(session: AsyncSession, place_id: int) -> List[Dict[str, Any]]:
        return list(
            map(
                lambda result: result._asdict(),
                await (
                    await session.stream(
                        Employees.__query()
                            .where(
                            EmployeesModel.place_id == place_id
                        ),
                    )
                ).all(),
            ),
        )
