# System imports
import json

# Dependency imports
from quart import Quart, request
from sqlalchemy.ext.asyncio import AsyncSession

# Own imports
from .config.logger_config import logger
from .utils.enviromental_variables import PORT
from .database import db_init, async_session
from .database import db_helper


application = Quart(__name__)

application.before_serving(db_init)


###### REQUEST HANDLERS ######

@application.route('/get_site_info', methods=['POST'])
async def interactive():
    data = json.loads(request.form.get('payload'))
    logger.debug("User requested site info")

    async with async_session() as session:
        session: AsyncSession

        all_places = db_helper.get_places_info(session)

    return all_places, 200


@application.route('/reset', methods=['POST'])
def reset():
    data = request.form
    return '', 200


###### WEB SERVER START ######
def manual_run():
    application.run(host='0.0.0.0', port=PORT)


# Put anything that you want to start from Gunicorn master proccess here
def on_starting(server):
    pass
