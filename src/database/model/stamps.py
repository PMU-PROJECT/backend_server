from sqlalchemy.schema import Column
from sqlalchemy.sql.functions import now
from sqlalchemy.types import DateTime

from . import ORMBase, id_ref_column
from .employees import Employees
from .places import Places
from .users import Users


class Stamps(ORMBase):
    visitor_id = id_ref_column(
        'visitor_id',
        Users.user_id,
        options={
            'primary_key': True,
        },
    )

    place_id = id_ref_column(
        'place_id',
        Places.place_id,
        options={
            'primary_key': True,
        },
    )

    employee_id = id_ref_column('employee_id', Employees.user_id, )

    given_on = Column(
        'given_on',
        DateTime(timezone=True, ),
        server_default=now(),
    )
