# System imports
import os
from os import path
from typing import List

# Dependency imports
from quart import Quart, request, send_file
# Own imports
from sqlalchemy import insert

from .app_logic import get_tourist_sites
from .auth import AuthenticationError, validate_token, verify_password, generate_token, hash_password
from .config.logger_config import logger
from .database import db_init, async_session
from .utils.enviromental_variables import PORT
from src.app_logic import get_site_by_id, get_tourist_sites, get_user_info
from .database.local_users import LocalUsers
from .database.model.local_users import LocalUsers as LocalUsersModel
from .database.model.users import Users as UsersModel
from .database.users import Users
from .google_api import google_api
from .utils.enviromental_variables import PORT

UNAUTHENTICATED_URLS: List[str] = [
    '/api/login',
    '/api/registration',
    '/api/oauth2/google',
]

application = Quart(__name__)

application.before_serving(db_init)
application.register_error_handler(AuthenticationError, lambda _: ({'error': 'Authentication failed!', }, 401,))


@application.before_request
def auth_before_request():
    if request.path not in UNAUTHENTICATED_URLS:
        request.authenticated_user = validate_token(request.headers.get('Authorization', None))


@application.route('/api/oauth2/google', methods=['GET'])
async def google_oauth2():
    print(google_api.authorization_url())
    print(request.args)

    raise AuthenticationError()

# ###### API REQUEST HANDLERS ######

# Tourist site endpoints

@application.route('/api/get_all_sites', methods=['GET'])
async def get_all_sites():
    args = request.args
    headers = request.headers

    # TODO check token
    if int(headers.get("Authorization")) != 3:
        return '', 401

    logger.debug("User requested all site info")

    async with async_session() as session:
        sites = await get_tourist_sites(session)

    return sites, 200


@application.route('/api/get_site_info', methods=['GET'])
async def get_site_info():
    args = request.args
    headers = request.headers

    print(f"token: {headers.get('Authorization')}")

    # TODO check token
    if int(headers.get("Authorization")) != 3:
        return '', 401

    logger.debug("User requested site detailed info")

    async with async_session() as session:
        site = await get_site_by_id(session, int(args.get("id")))

    return site, 200


# Login and registration endpoints


@application.route('/api/registration', methods=['POST'])
async def registration():
    form = await request.json

    first_name = form.get('first_name')
    last_name = form.get('last_name')
    email = form.get('email')
    password = form.get('password')

    if None in (first_name, last_name, email, password):
        return 'insufficient information', 422

    async with async_session() as session:
        if await Users.exists_by_email(session, email):
            return {'error': 'User with this email already exists!'}, 400

        user_id: int = (
            await session.execute(
                insert(
                    UsersModel,
                ).values(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                ).returning(
                    UsersModel.id,
                ),
            )
        ).scalar()

        await session.execute(
            insert(
                LocalUsersModel,
            ).values(
                user_id=user_id,
                pw_hash=hash_password(password),
            ),
        )

        await session.commit()

        return {
                   'token': generate_token(user_id, ),
               }, 200


@application.route('/api/login', methods=['POST'])
async def login():
    form = await request.json

    email = form.get('email')
    password = form.get('password')

    if None in (email, password):
        return 'insufficient information', 422

    async with async_session() as session:
        user_id, pw_hash = await LocalUsers.by_email(session, email)

        if verify_password(password, pw_hash):
            return {
                'token': generate_token(user_id),
            }

        raise AuthenticationError()


@application.route('/api/google_login', methods=['POST'])
async def google_login():
    form = await request.json

    google_token = form.get('token')

    if google_token is None:
        return 'insufficient information', 422

    # TODO API call to google for user info
    # TODO if not valid return error code

    # TODO if valid, check if user exists locally
    # TODO return token if yes
    # TODO make user and return token if no

    return {'token': '3'}, 200


# User info endpoint
@application.route('/api/get_user_info', methods=['GET'])
async def user_info():
    headers = request.headers

    # TODO decode token, if valid and user exists
    id = int(headers.get("Authorization"))

    if id != 3:
        return '', 401

    # TODO return user info
    # TODO else return error code

    async with async_session() as session:
        session: AsyncSession
        user = await get_user_info(session, id)

    return user


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
