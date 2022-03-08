# System imports
import os
from os import path

# Dependency imports
from quart import Quart, request, send_file
from sqlalchemy.ext.asyncio import AsyncSession

# Own imports
from .app_logic import get_tourist_sites
from .config.logger_config import logger
from .database import db_init, async_session
from .utils.enviromental_variables import PORT
from .google_api import google_api

application = Quart(__name__)

application.before_serving(db_init)


@application.route('/api/oauth2/google', ['GET'])
async def google_oauth2():
    print(google_api.authorization_url())
    print(request.args)

    return {}, 200


# ###### API REQUEST HANDLERS ######
@application.route('/api/get_all_sites', methods=['GET'])
async def get_all_sites():
    args = request.args
    headers = request.headers
    # TODO check token

    logger.debug("User requested site info")

    async with async_session() as session:
        session: AsyncSession
        sites = await get_tourist_sites(session)

    return sites, 200


# ###### IMAGE SERVER HANDLERS ######


@application.route('/imageserver/tourist_sites', methods=['GET'])
async def tourist_site_photo():
    '''
    based on an 'pic_name' arg, send back a photo from public/tourist_sites folder.
    Requires Auth token
    '''
    args = request.args
    headers = request.headers

    # TODO check token
    if headers.get('Authorization') is None:
        return '', 401

    if args.get('pic_name') is not None:
        file_path = os.path.join(
            'public', 'tourist_sites', args.get('pic_name'))

        if path.isfile(file_path):
            return await send_file(file_path, mimetype='image/gif')
        else:
            return '', 404

    return '', 200


@application.route('/imageserver/profile_pictures', methods=['GET'])
async def profile_pictures():
    args = request.args
    headers = request.headers

    # TODO check token
    if headers.get('Authorization') is None:
        return '', 401

    if args.get('pic_name') is not None:
        file_path = os.path.join(
            'public', 'profile_pictures', args.get('pic_name'))

        if path.isfile(file_path):
            return await send_file(file_path, mimetype='image/gif')
        else:
            return '', 404

    return '', 200


# ###### WEB SERVER START ######
def manual_run():
    application.run(host='0.0.0.0', port=PORT, debug=True)


# Put anything that you want to start from Gunicorn master process here
def on_starting(server):
    pass
