from typing import Any, Dict

import simplejson as json
from sqlalchemy.ext.asyncio import AsyncSession

from .database.administrators import Administrators
from .database.employees import Employees
from .database.images import Images
from .database.places import Places
from .database.stamps import Stamps
from .database.users import Users
from .utils.all_sites_filter import AllSitesFilter


async def get_tourist_sites(session: AsyncSession, site_type: AllSitesFilter, visitor_id: int):
    """
    Function for creating a JSON-able dictionary, containing data for all the tourist sites in the Database.
    Includes Place, City, Region, connected Images and connected Employee ID's

    params:
        session : AsyncSession -> Session to the database
        type : AllSitesTypes -> list of what sites should be returned
        visitor_id : int -> user_id in the database, to whom we will compare the visited and unvisited sites

    returns:
        dictionary, with a key value 'sites' and value a list, containing the tourist sites
    """
    sites_db = await Places.all(session)

    # get place_id of visited sites
    stamps_db = await Stamps.all(session, visitor_id)
    stamp_places_id = [stamp['place_id'] for stamp in stamps_db]

    sites_jsonable = {'sites': []}

    for site in sites_db:

        # Skip all unvisited
        if site_type == AllSitesFilter.visited:
            if site.get('id') not in stamp_places_id:
                continue

        # Skip all visited
        if site_type == AllSitesFilter.unvisited:
            if site.get('id') in stamp_places_id:
                continue

        current_site = {
            'image': (
                await Images.all_by_place(
                    session, site.get('id'),
                )
            )[0],
            'region': site['region_name'],
            'city': site['city_name'],
            'name': site['name'],
        }

        # get only 1 image for visualisation of the card

        # Other variables
        # current_site['description'] = site['description']

        # append the dictionary in the list after writing all the vars
        sites_jsonable['sites'].append(current_site)

    return sites_jsonable


async def get_site_by_id(session: AsyncSession, site_id: int):
    """
    Function for creating JSON-able site
    """

    site: Dict[str, Any] = await Places.by_id(session, site_id)

    if site is None:
        return None

    return {
        # lists
        'images': await Images.all_by_place(
            session,
            site.get('id'),
        ),
        'employees': await Employees.all_by_place(
            session,
            site.get('id'),
        ),
        # Make latitude and longitude JSON serializable
        'latitude': json.dumps(
            site['latitude'],
            use_decimal=True,
        ),
        'longitude': json.dumps(
            site['longitude'],
            use_decimal=True,
        ),
        # Other variables
        'region': site['region_name'],
        'city': site['city_name'],
        'name': site['name'],
        'description': site['description'],
    }


async def get_user_info(session: AsyncSession, user_id: int):
    """
    Function for generating JSON-able user info
    """

    user = dict(await Users.by_id(session, user_id))

    # if None, no point in continuing
    if user is None:
        return None

    # Needed requests
    user['stamps'] = await Stamps.all(session, user_id)
    user['employee_info'] = await Employees.by_id(session, user_id)
    user['is_admin'] = bool(await Administrators.exists(session, user_id))

    return user


async def get_employee_info(session: AsyncSession, employee_id: int):
    """
    Function for getting JSON-able employee info
    """

    employee_info = await Employees.by_id(session, employee_id)

    # if None, no point in continuing
    if employee_info is None:
        return None

    # Needed requests
    employee_info['is_admin'] = await Administrators.exists(session, employee_id)

    return employee_info