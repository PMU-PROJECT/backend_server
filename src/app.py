# System imports
import os
from os import path
from re import match
from typing import List

# Dependency imports
from quart import Quart, request, send_file, g
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from quart_cors import cors

# Own imports
from .app_logic import get_employee_info, get_site_by_id, get_tourist_sites, get_user_info
from .auth import AuthenticationError, validate_token, verify_password, generate_token, hash_password
from .config.logger_config import logger
from .database import db_init, async_session
from .database.local_users import LocalUsers
from .database.model.local_users import LocalUsers as LocalUsersModel
from .database.model.users import Users as UsersModel
from .database.users import Users
from .google_api import google_api
from .utils.enviromental_variables import PORT
from .utils.all_sites_types import AllSitesTypes

UNAUTHENTICATED_URLS: List[str] = [
    '/api/login',
    '/api/registration',
    '/api/oauth2/google',
]

application = Quart(__name__, )
application = cors(
    application,
    allow_origin="*",
    allow_headers=['Authorization', 'Content-type', ],
    allow_methods=['GET', 'POST', ],
)

application.before_serving(db_init, )
application.register_error_handler(
    AuthenticationError,
    lambda _: (
        {'error': 'Authentication failed!', }, 401
    ),
)


@application.before_request
def auth_before_request():
    """
    """
    if request.path not in UNAUTHENTICATED_URLS:
        try:
            g.authenticated_user = int(
                validate_token(
                    request.headers.get('Authorization', None, )
                )
            )
        except ValueError:
            raise AuthenticationError()


# ###### API REQUEST HANDLERS ######

# Tourist site endpoints


@application.route('/api/get_all_sites', methods=['GET', ], )
async def get_all_sites():

    site_type = request.args.get('type', type=str, )

    try:
        site_type = AllSitesTypes(site_type)
    except ValueError:
        return {"error": "Incorrect information",
                "expected": "'type' : 'all' / 'visited' / 'unvisited' as an argument"}, 400

    logger.debug("User requested all site info", )

    async with async_session() as session:
        sites = await get_tourist_sites(session, site_type, g.authenticated_user)

    return sites, 200


@application.route('/api/get_site_info', methods=['GET', ], )
async def get_site_info():
    site_id = request.args.get('id', type=int, )

    logger.debug("User requested site detailed info", )

    async with async_session() as session:
        site = await get_site_by_id(session, site_id)

    return (site, 200) if site is not None else ({"error": "Site not found", }, 404)


# Login and registration endpoints


@application.route('/api/registration', methods=['POST', ], )
async def registration():
    form = await request.form

    first_name = form.get('first_name', type=str, )
    last_name = form.get('last_name', type=str, )
    email = form.get('email', type=str, )
    password = form.get('password', type=str, )

    if None in (first_name, last_name, email, password,):
        return {
            'error': 'insufficient information',
            'expected': [
                'first_name',
                'last_name',
                'email',
                'password',
            ],
        }, 422

    if len(password, ) < 6:
        return {'error': 'Password too short. It must be 6 characters or longer', }, 400

    async with async_session() as session:
        if await Users.exists_by_email(session, email, ):
            return {'error': 'User with this email already exists!', }, 400

        try:
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
        except IntegrityError:
            return {"error": "Email not valid", }, 400

        await session.execute(
            insert(
                LocalUsersModel,
            ).values(
                user_id=user_id,
                pw_hash=hash_password(password, ),
            ),
        )

        await session.commit()

        return {'token': generate_token(user_id, ), }, 200


@application.route('/api/login', methods=['POST', ], )
async def login():
    form = await request.form

    if form is None:
        return {"error": "Wrong request body!"}

    email = form.get('email', type=str, )
    password = form.get('password', type=str, )

    if None in (email, password,):
        return {"error": "Insufficient information", }, 422

    async with async_session() as session:
        user_id, pw_hash = await LocalUsers.by_email(session, email, )

        if verify_password(password, pw_hash, ):
            return {'token': generate_token(user_id, ), }, 200

        # returns 400 error
        raise AuthenticationError()


@application.route('/api/oauth2/google', methods=['GET', ], )
async def google_oauth2():
    print(google_api.authorization_url(), )
    print(request.args, )

    raise AuthenticationError()


@application.route('/api/refresh-token', methods=['GET', ], )
async def refresh_token():
    return {'token': generate_token(g.authenticated_user, ), }, 200


# User info endpoint

@application.route('/api/get_self_info', methods=['GET', ], )
async def self_info():
    user_id = g.authenticated_user

    async with async_session() as session:
        user = await get_user_info(session, user_id, )

    return user


@application.route('/api/get_user_info', methods=['GET', ], )
async def user_info():
    user_id = request.args.get('id', type=int, )

    if user_id is None:
        return {"error": "Insufficient information", }, 422

    async with async_session() as session:
        employee = await get_employee_info(session, user_id, )
        return ({"error": "Employee doesn't exist!", }, 404) if employee is None else (employee, 200)


# ###### IMAGE SERVER HANDLERS ######


@application.route('/imageserver/tourist_sites', methods=['GET', ], )
async def tourist_site_photo():
    """
    based on an 'name' arg, send back a photo from public/tourist_sites folder.
    Requires Authorization header
    """
    name = request.args.get('name', type=str, )

    if name is not None:
        if match(r'^[\w\s_+\-()]([\w\s_+\-().])+$', name) is None:
            return {"error": "Invalid site picture!", }, 400

        file_path = os.path.join(
            'public',
            'tourist_sites',
            name,
        )

        if path.isfile(file_path, ):
            return await send_file(file_path, mimetype='image/gif', )
        else:
            return {"error": "Picture not found", }, 404

    return {"error": "Insufficient information!", }, 422


@application.route('/imageserver/profile_pictures', methods=['GET', ], )
async def profile_pictures():
    name = request.args.get('name', type=str, )

    if name is not None:
        if match(r'^[\w\s_+\-()]([\w\s_+\-().])+$', name) is None:
            return {"error": "Invalid site picture!", }, 400

        file_path = os.path.join(
            'public',
            'profile_pictures',
            name,
        )

        if path.isfile(file_path):
            return await send_file(file_path, mimetype='image/gif', )
        else:
            return {"error": "Picture not found", }, 404

    return {"error": "Insufficient information!", }, 422


# ###### WEB SERVER START ######
def manual_run():
    application.run(host='0.0.0.0', port=PORT, debug=True, )


# Put anything that you want to start from Gunicorn master process here
def on_starting(server):
    pass
