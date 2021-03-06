from typing import Any, Dict

import simplejson as json
from sqlalchemy.ext.asyncio import AsyncSession

from .database.reward_types import RewardTypes
from .database.rewards_log import RewardsLog
from .database.administrators import Administrators
from .database.employees import Employees
from .database.images import Images
from .database.places import Places
from .database.stamps import Stamps
from .database.users import Users
from .utils.all_sites_filter import AllSitesFilter
from .config.logger_config import logger
from .id_token import get_id_from_token


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
            if site.get('place_id') not in stamp_places_id:
                continue

        # Skip all visited
        if site_type == AllSitesFilter.unvisited:
            if site.get('place_id') in stamp_places_id:
                continue

        # Fetch image id
        image_id = await Images.first_by_place(session, site.get('place_id'))

        current_site = {
            'id': site['place_id'],
            'image': image_id,
            'region': site['region_name'],
            'city': site['city_name'],
            'name': site['name'],
            'is_stamped': bool(site.get('place_id') in stamp_places_id)
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
            site.get('place_id'),
        ),
        'employees': await Employees.all_by_place(
            session,
            site.get('place_id'),
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


async def get_self_info(session: AsyncSession, user_id: int):
    """
    Function for generating JSON-able user info
    """

    user = await Users.by_id(session, user_id)

    # if None, no point in continuing
    if user is None:
        return None

    # Needed requests
    user.update(
        stamps=await Stamps.all(
            session,
            user_id,
        ),
        employee_info=await Employees.by_id(
            session,
            user_id,
        ),
        is_admin=await Administrators.exists(
            session,
            user_id,
        ),
        given_rewards=await RewardsLog.all_by_visitor_id(
            session,
            user_id,
        ),
        eligible_rewards=await RewardTypes.eligible(
            session,
            user_id,
        ),
    )

    return user


async def get_user_info(session: AsyncSession, user_id: int):
    """
    Function for generating JSON-able user info
    """

    user_db = dict(await Users.by_id(session, user_id))

    # if None, no point in continuing
    if user_db is None:
        return None

    return {
        'first_name': user_db.get('first_name'),
        'last_name': user_db.get('last_name'),
        'profile_picture': user_db.get('profile_picture'),
        'is_employee': bool(await Employees.exists(session, user_id)),
        'is_admin': bool(await Administrators.exists(session, user_id))
    }


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


async def get_user_eligible_rewards(session: AsyncSession, id_token: str):
    visitor_id = get_id_from_token(id_token)
    logger.debug(f"ID: {visitor_id}")

    stamps = await Stamps.all(session, visitor_id)
    logger.debug(f"Stamps count : {len(stamps)}")

    received_rewards = await RewardsLog.all_by_visitor_id(session, visitor_id)
    logger.debug(f"Received num of rewards : {len(received_rewards)}")

    return {
        "received_rewards": received_rewards,
        "eligible_rewards": await RewardTypes.eligible(
            session,
            visitor_id,
        )
    }
