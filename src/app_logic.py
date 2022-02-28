from sqlalchemy.ext.asyncio import AsyncSession

from .database.model.places import Places
from .database.model.employees import Employees
from .database.model.images import Images
from src.database.model import employees


def get_tourist_sites(session: AsyncSession):
    '''
    DUMMY FUNCTION
    shows how to create logic for program

    Make connection with DB
    get tourist sites info
    return it
    '''
    all_sites = Places.all(session)

    for i, site in enumerate(all_sites):
        images = Images.all_by_place(site.get('id'))
        employees = Employees.all_by_place(site.get('id'))

        all_sites[i]['images'] = images
        all_sites[i]['employees'] = employees

    return all_sites
