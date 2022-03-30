from typing import Any, Dict, List, Optional, Union

from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select, Select

from .model.cities import Cities as CitiesModel
from .model.places import Places as PlacesModel
from .model.regions import Regions as RegionsModel


class Places(object):
    @staticmethod
    def __query() -> Select:
        return select(
            [RegionsModel.name.label('region_name'), CitiesModel.name.label('city_name'), PlacesModel.id,
                PlacesModel.name.label('name'), PlacesModel.description, PlacesModel.latitude, PlacesModel.longitude, ],
            from_obj=PlacesModel, ).join(
            CitiesModel, PlacesModel.city_id == CitiesModel.id, ).join(
            RegionsModel, CitiesModel.region_id == RegionsModel.id, )

    @staticmethod
    async def by_id(session: AsyncSession, place_id: int) -> Optional[Dict[str, Any]]:
        result: Union[None, Row] = (await session.execute(
            Places.__query().where(
                PlacesModel.id == place_id, ), )).first()

        return None if result is None else result._asdict()

    @staticmethod
    async def all(session: AsyncSession) -> List[Dict[str, Any]]:
        return list(
            map(
                lambda result: result._asdict(), await (await session.stream(
                    Places.__query(), )).all(), ), )
