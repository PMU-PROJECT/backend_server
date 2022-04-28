from sqlalchemy.schema import Column
from sqlalchemy.types import Boolean

from . import ORMBase, id_ref_column
from .administrators import Administrators
from .places import Places
from .users import Users


class Employees(ORMBase):
    user_id = id_ref_column('user_id', Users.user_id, options={'primary_key': True, }, )

    place_id = id_ref_column('place_id', Places.place_id, )

    added_by = id_ref_column('added_by', Administrators.user_id, )

    can_reward = Column('can_reward', Boolean(create_constraint=True, ), )
