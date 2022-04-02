from sqlalchemy.schema import Column
from sqlalchemy.types import Unicode, Integer
from sqlalchemy import String

from . import ORMBase, id_column


class RewardTypes(ORMBase):
    id = id_column('reward_id', )

    name = Column('name', Unicode(127, ), )

    description = Column('description', Unicode(511, ), )

    minimum_stamps = Column('minimum_stamps', Integer())

    picture = Column(
        'picture',
        String(127, ),
        default='default_profile_pic.png',
    )
