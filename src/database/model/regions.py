from sqlalchemy.schema import Column
from sqlalchemy.types import Unicode

from . import ORMBase, id_column


class Regions(ORMBase):
    id = id_column('region_id', )

    name = Column('name', Unicode(255, ), )
