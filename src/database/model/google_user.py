from sqlalchemy.schema import Column
from sqlalchemy.sql.sqltypes import UnicodeText

from . import ORMBase, id_ref_column
from .users import Users


class GoogleUsers(ORMBase):
    user_id = id_ref_column(
        'user_id',
        Users.user_id,
        options={
            'primary_key': True,
        },
    )

    google_id = Column(
        'google_id',
        UnicodeText(),
        nullable=False,
    )
