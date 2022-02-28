from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select

from .model.cities import Cities as CitiesModel
from .model.places import Places as PlacesModel
from .model.regions import Regions as RegionsModel


class Places(object):
    async def all(session: AsyncSession) -> List[Dict[str, Any]]:
        return list(
            map(
                lambda result: result._asdict(),
                (
                    await session.stream(
                        select(
                            [
                                RegionsModel.name,
                                CitiesModel.name,
                                PlacesModel.name,
                                PlacesModel.name,
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
                        ),
                    )
                ).all(),
            ),
        )
