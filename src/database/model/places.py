from sqlalchemy import TEXT
from sqlalchemy.schema import Column
from sqlalchemy.types import Numeric, Unicode

from . import ORMBase, id_column, id_ref_column
from .cities import Cities


class Places(ORMBase):

    city_id = id_ref_column('city_id', Cities.city_id, )

    place_id = id_column('place_id', )

    name = Column('name', Unicode(255, ), )

    description = Column('description', TEXT())

    latitude = Column(
        'latitude',
        Numeric(
            precision=10,
            scale=6,
            asdecimal=True,
        ),
    )

    longitude = Column(
        'longitude',
        Numeric(
            precision=10,
            scale=6,
            asdecimal=True,
        ),
    )
