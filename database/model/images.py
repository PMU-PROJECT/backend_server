from sqlalchemy.schema import Column
from sqlalchemy.types import LargeBinary

from . import ORMBase, id_column, id_ref_column
from .places import Places


class Images(ORMBase):
    place_id = id_ref_column('place_id', Places.id,)

    id = id_column('image_id',)

    data = Column('name', LargeBinary(),)
