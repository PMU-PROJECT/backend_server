from typing import Any, Dict, List, Union

from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Join
from sqlalchemy.sql.expression import select

from .model.cities import Cities as CitiesModel
from .model.places import Places as PlacesModel
from .model.regions import Regions as RegionsModel


class Places(object):
    @staticmethod
    def __query() -> Join:
        return select(
            [
                RegionsModel.name,
                CitiesModel.name,
                PlacesModel.id,
                PlacesModel.name,
                PlacesModel.description,
                PlacesModel.latitude,
                PlacesModel.longitude,
            ],
            from_obj=PlacesModel,
        ).join(
            CitiesModel,
            PlacesModel.city_id == CitiesModel.id,
        ).join(
            RegionsModel,
            CitiesModel.region_id == RegionsModel.id,
        )

    @staticmethod
    async def by_id(session: AsyncSession, place_id: int) -> Union[None, Dict[str, Any]]:
        result: Union[None, Row] = (
            await session.execute(
                Places.__query()
                    .where(
                    PlacesModel.id == place_id,
                ),
            )
        ).first()

        return None if result is None else result._asdict()

    @staticmethod
    async def all(session: AsyncSession) -> List[Dict[str, Any]]:
        return list(
            map(
                lambda result: result._asdict(),
                await (
                    await session.stream(
                        Places.__query(),
                    )
                ).all(),
            ),
        )
