from sqlalchemy.ext.asyncio import AsyncSession

from .database.places import Places
from .database.employees import Employees
from .database.images import Images


async def get_tourist_sites(session: AsyncSession):
    '''
    DUMMY FUNCTION
    shows how to create logic for program

    Make connection with DB
    get tourist sites info
    return it
    '''
    all_sites = await Images.all_by_place(session, 1)
    print(all_sites)
    print(type(all_sites))

    '''
    for i, site in enumerate(all_sites):
        images = Images.all_by_place(site.get('id'))
        employees = Employees.all_by_place(site.get('id'))

        all_sites[i]['images'] = images
        all_sites[i]['employees'] = employees
    '''

    return all_sites
