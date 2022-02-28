from .model.users import Users

from sqlalchemy.ext.asyncio import AsyncSession


@staticmethod
def get_all_places_info(session):
    '''


    params:
        session: Session to the database
        place_id: If none, returns all places, else returns given place (or None)

    returns:
        list of dictionaries, containing every tourist site  (JSON-able)
    '''
    all_places = []


@staticmethod
def get_place_info(session: AsyncSession, place_id):
    pass


@staticmethod
def get_user_info(session: AsyncSession, user_id):
    '''

    params:
        session: Session to the database
        user_id: primary key of the user

    returns:
        dictionary containing everything about the user
    '''
    pass


@staticmethod
def get_user_login(session, user_id):
    pass
