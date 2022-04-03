from typing import Any, Dict, List, Optional, Union

from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select, Select

from .model.cities import Cities as CitiesModel
from .model.places import Places as PlacesModel
from .model.regions import Regions as RegionsModel
from ..exceptions import DatabaseError


class Places(object):
    @staticmethod
    def __query() -> Select:
        return select(
            [RegionsModel.name.label('region_name'), CitiesModel.name.label('city_name'), PlacesModel.place_id,
                PlacesModel.name.label('name'), PlacesModel.description, PlacesModel.latitude, PlacesModel.longitude, ],
        ).select_from(
            PlacesModel,
        ).join(
            CitiesModel, PlacesModel.city_id == CitiesModel.city_id, ).join(
            RegionsModel, CitiesModel.region_id == RegionsModel.region_id, )

    @staticmethod
    async def by_id(session: AsyncSession, place_id: int) -> Optional[Dict[str, Any]]:
        try:
            result: Union[None, Row] = (await session.execute(
                Places.__query().where(
                    PlacesModel.place_id == place_id, ), )).first()
        except Exception as ex:
            raise DatabaseError(ex)

        return None if result is None else {
            col: getattr(result, col)
            for col in result.keys()
        }

    @staticmethod
    async def all(session: AsyncSession) -> List[Dict[str, Any]]:
        try:
            return list(
                map(
                    lambda result: {
                        col: getattr(result, col)
                        for col in result.keys()
                    }, await (
                        await session.stream(
                            Places.__query(),
                        )
                    ).all(),
                ),
            )
        except Exception as ex:
            raise DatabaseError(ex)
