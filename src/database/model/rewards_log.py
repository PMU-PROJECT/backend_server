from sqlalchemy.schema import Column
from sqlalchemy.sql.functions import now
from sqlalchemy.types import DateTime

from . import ORMBase, id_ref_column
from .employees import Employees
from .reward_types import RewardTypes
from .users import Users


class RewardsLog(ORMBase):
    visitor_id = id_ref_column(
        'visitor_id', Users.id, options={
            'primary_key': True, }, )

    employee_id = id_ref_column('employee_id', Employees.id, )

    reward_id = id_ref_column(
        'reward_id', RewardTypes.id, options={
            'primary_key': True, }, )

    given_on = Column('given_on', DateTime(
        timezone=True, ), server_default=now(), )
