from sqlalchemy import LargeBinary
from sqlalchemy.schema import Column

from . import ORMBase, id_ref_column
from .users import Users


class LocalUsers(ORMBase):
    user_id = id_ref_column('user_id', Users.user_id, options={'primary_key': True, }, )

    pw_hash = Column(
        'pw_hash',
        LargeBinary(),
        nullable=False,
    )
