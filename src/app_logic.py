import simplejson as json
from sqlalchemy.ext.asyncio import AsyncSession

from .database.employees import Employees
from .database.images import Images
from .database.places import Places
from .database.users import Users
from .database.stamps import Stamps
from .database.administrators import Administrators


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

        # get only 1 image for visualisation of the card
        current_site['image'] = (await Images.all_by_place(session, site.get('id')))[0]

        # Other variables
        current_site['region'] = site['name']
        current_site['city'] = site['name_1']
        current_site['name'] = site['name_2']
        #current_site['description'] = site['description']

        # append the dictionary in the list after writing all the vars
        sites_jsonable['sites'].append(current_site)

    return sites_jsonable


async def get_site_by_id(session: AsyncSession, id: int):
    '''
    Function for creating JSON-able site
    '''
    site = await Places.by_id(session, id)

    if site is None:
        return None

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
    user['stamps'] = await Stamps.all(session, id)
    user['employee_info'] = await Employees.by_id(session, id)
    user['is_admin'] = bool(await Administrators.exists(session, id))

    if user.get('employee_info') is not None:
        user['employee_info']['added_by'] = await Users.by_id(session, int(user['employee_info'].get('added_by')))

    return user


async def get_employee_info(session: AsyncSession, id: int):
    '''
    Function for getting employee info
    '''

    employee_info = await Employees.by_id(session, id)

    # if None, no point in continuing
    if employee_info is None:
        return None

    # Needed requests
    employee_info['is_admin'] = bool(await Administrators.exists(session, id))
    employee_info['added_by'] = await Users.by_id(session, int(employee_info.get('added_by')))

    return employee_info
