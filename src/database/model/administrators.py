from . import ORMBase, id_ref_column
from .users import Users


class Administrators(ORMBase):
    id = id_ref_column('user_id', Users.id, options={'primary_key': True, },)
