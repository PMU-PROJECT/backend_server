from sqlalchemy import Text
from sqlalchemy.schema import Column
from sqlalchemy.types import Numeric, Unicode

from . import ORMBase, id_column, id_ref_column
from .regions import Regions


class Places(ORMBase):
    region_id = id_ref_column('region_id', Regions.id,)

    city_id = id_ref_column('city_id', Regions.id,)

    id = id_column('place_id',)

    name = Column('name', Unicode(255,),)

    description = Column('description', Text(),)

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
