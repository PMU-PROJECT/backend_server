import simplejson as json
from sqlalchemy.ext.asyncio import AsyncSession

from .database.employees import Employees
from .database.images import Images
from .database.places import Places


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
        print(site['id'])

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
