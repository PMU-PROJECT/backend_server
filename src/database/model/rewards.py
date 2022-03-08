from sqlalchemy.schema import Column
from sqlalchemy.types import Unicode

from . import ORMBase, id_column


class Rewards(ORMBase):
    id = id_column('reward_id', )

    name = Column('name', Unicode(127, ), )

    description = Column('description', Unicode(511, ), )
