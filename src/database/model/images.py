from sqlalchemy import String
from sqlalchemy.schema import Column

from . import ORMBase, id_column, id_ref_column
from .places import Places


class Images(ORMBase):
    place_id = id_ref_column('place_id', Places.place_id, )

    image_id = id_column('image_id', )

    filename = Column('filename', String(127), )
