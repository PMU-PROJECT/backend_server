from sqlalchemy import String, UniqueConstraint
from sqlalchemy.schema import Column, CheckConstraint
from sqlalchemy.types import Unicode

from . import ORMBase, id_column


class Users(ORMBase):
    user_id = id_column('user_id', )

    first_name = Column('first_name', Unicode(127, ), )

    last_name = Column('last_name', Unicode(127, ), )

    email = Column(
        'email',
        Unicode(255, ),
        CheckConstraint("email ~* '^\\w+@(?:\\w+.)*\\w+$'", ),
        UniqueConstraint(),
    )

    profile_picture = Column(
        'profile_picture',
        String(127, ),
        default='default_profile_pic.png',
    )
