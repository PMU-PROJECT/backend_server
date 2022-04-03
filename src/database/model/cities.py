from sqlalchemy.schema import Column
from sqlalchemy.types import Unicode

from . import ORMBase, id_column, id_ref_column
from .regions import Regions


class Cities(ORMBase):
    region_id = id_ref_column('region_id', Regions.region_id, )

    city_id = id_column('city_id', )

    name = Column('name', Unicode(255, ), )
