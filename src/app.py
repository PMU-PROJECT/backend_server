# System imports
import json

# Dependency imports
from quart import Quart, request
from sqlalchemy.ext.asyncio import AsyncSession

from src.app_logic import get_tourist_sites

# Own imports
from .config.logger_config import logger
from .utils.enviromental_variables import PORT
from .database import db_init, async_session


application = Quart(__name__)

application.before_serving(db_init)


###### REQUEST HANDLERS ######

@application.route('/api/get_all_sites', methods=['POST'])
async def get_all_sites():
    data = await request.form
    # TODO check token

    logger.debug("User requested site info")

    async with async_session() as session:
        session: AsyncSession
        sites = await get_tourist_sites(session)

    return sites, 200


@application.route('/api/pictures', methods=['POST'])
async def reset():
    data = await request.form
    print(data)

    return '', 200


###### WEB SERVER START ######
def manual_run():
    application.run(host='0.0.0.0', port=PORT, debug=True)


# Put anything that you want to start from Gunicorn master proccess here
def on_starting(server):
    pass
