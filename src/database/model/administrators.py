from . import ORMBase, id_ref_column
from .users import Users


class Administrators(ORMBase):
    user_id = id_ref_column('user_id', Users.user_id, options={'primary_key': True, }, )
