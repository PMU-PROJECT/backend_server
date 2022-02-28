from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select

from .model.employees import Employees as EmployeesModel
from .model.users import Users as UsersModel


class Employees(object):
    @staticmethod
    async def all_by_place(session: AsyncSession, id: int) -> List[Dict[str, Any]]:
        return list(
            map(
                lambda result: result._asdict(),
                (
                    await session.execute(
                        select(
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
                        ).where(
                            EmployeesModel.place_id == id
                        ),
                    )
                ).all(),
            ),
        )
