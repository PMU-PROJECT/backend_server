import simplejson as json
from sqlalchemy.ext.asyncio import AsyncSession

from .database.employees import Employees
from .database.images import Images
from .database.places import Places
from .database.users import Users
from .database.stamps import Stamps
from .database.administrators import Administrators
from src.database import users


async def get_tourist_sites(session: AsyncSession):
    '''
    Function for creating a JSON-able dictionary, containing data for all the tourist sites in the Database.
    Includes Place, City, Region, connected Images and connected Employee ID's

    params:
        session : AsyncSession -> Session to the database

    returns:
        dictionary, with a key value 'sites' and value a list, containing the tourist sites
    '''
    sites_db = await Places.all(session)
    sites_jsonable = {'sites': []}

    for site in sites_db:
        current_site = {}
        # lists
        current_site['images'] = await Images.all_by_place(session, site.get('id'))
        current_site['employees'] = await Employees.all_by_place(session, site.get('id'))

        # Make latitude and longitude JSON serializable
        current_site['latitude'] = json.dumps(
            site['latitude'], use_decimal=True)
        current_site['longitude'] = json.dumps(
            site['longitude'], use_decimal=True)

        # Other variables
        current_site['region'] = site['name']
        current_site['city'] = site['name_1']
        current_site['name'] = site['name_2']
        current_site['description'] = site['description']

        # append the dictionary in the list after writing all the vars
        sites_jsonable['sites'].append(current_site)

    return sites_jsonable


async def get_site_by_id(session: AsyncSession, id: int):
    '''
    Function for creating JSON-able site
    '''
    site = await Places.by_id(session, id)

    if site is None:
        return {}

    current_site = {}

    # lists
    current_site['images'] = await Images.all_by_place(session, site.get('id'))
    current_site['employees'] = await Employees.all_by_place(session, site.get('id'))

    # Make latitude and longitude JSON serializable
    current_site['latitude'] = json.dumps(
        site['latitude'], use_decimal=True)
    current_site['longitude'] = json.dumps(
        site['longitude'], use_decimal=True)

    # Other variables
    current_site['region'] = site['name']
    current_site['city'] = site['name_1']
    current_site['name'] = site['name_2']
    current_site['description'] = site['description']

    return current_site


async def get_user_info(session: AsyncSession, id: int):
    '''
    Function for generating JSON-able user info
    '''

    user = dict(await Users.by_id(session, id))

    # if None, no point in continuing
    if user is None:
        return None

    # Needed requests
    stamps = await Stamps.all(session, id)
    employee_info = await Employees.by_id(session, id)
    is_admin = await Administrators.exists(session, id)

    user['stamps'] = stamps
    user['employee_info'] = employee_info
    user['is_admin'] = bool(is_admin)

    return user
