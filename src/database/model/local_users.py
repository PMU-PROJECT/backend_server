from sqlalchemy.schema import Column
from sqlalchemy.types import String

from . import ORMBase, id_ref_column
from .users import Users


class LocalUsers(ORMBase):
    id = id_ref_column('user_id', Users.id, options={'primary_key': True, }, )

    pw_hash = Column('pw_hash', String(), )
