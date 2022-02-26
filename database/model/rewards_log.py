from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime

from . import ORMBase, id_ref_column
from .employees import Employees
from .rewards import Rewards
from .users import Users


class RewardsLog(ORMBase):
    visitor_id = id_ref_column(
        'visitor_id', Users.id, options={
            'primary_key': True, },)

    employee_id = id_ref_column('employee_id', Employees.id,)

    reward_id = id_ref_column(
        'reward_id', Rewards.id, options={
            'primary_key': True, },)

    given_on = Column('given_on', DateTime(timezone=True,),)
