# System imports
import os
from os import path
from re import match
from typing import List, Any, Dict, Optional, Tuple

# Dependency imports
from quart import Quart, request, send_file, g
from quart_cors import cors
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError

# Own imports
from .app_logic import get_employee_info, get_site_by_id, get_tourist_sites, get_user_info
from .auth import AuthenticationError, validate_token, verify_password, generate_token, hash_password
from .config.logger_config import logger
from .database import db_init, async_session
from .database.employees import Employees
from .database.local_users import LocalUsers
from .database.model.local_users import LocalUsers as LocalUsersModel
from .database.model.users import Users as UsersModel
from .database.stamps import Stamps
from .database.users import Users
from .google_api import google_api
from .stamps import generate_stamp_token, finish_stamping, Stamp
from .utils.all_sites_filter import AllSitesFilter
from .utils.enviromental_variables import PORT

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

# Initialize connection and make tables if not exist
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
    Validates JWT token in Authorization header. Executes before every
    protected endpoint
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
    """
    Function for getting basic info on many sites.

    params:
        arg 'filter' : str -> all, visited or unvisited

    returns:
    'sites' : [
        {
            'city':str,
            'image':str,
            'name':str,
            'region':str
        },
    ]

    excepts:
        401: JWT token not valid
        400: filter not valid
    """

    site_type = request.args.get('filter', type=str, )

    try:
        site_type = AllSitesFilter(site_type)
    except ValueError:
        # TODO make expected synced with ENUM
        return {"error": "Incorrect information",
                "expected": "'filter' : 'all' / 'visited' / 'unvisited' as an argument"}, 400

    logger.debug("User requested all site info", )

    async with async_session() as session:
        sites = await get_tourist_sites(session, site_type, g.authenticated_user)

    return sites, 200


@application.route('/api/get_site_info', methods=['GET', ], )
async def get_site_info():
    """
    Get detailed info on a certain tourist site

    arg 'id' : int -> place_id of needed site

    returns JSON list:
        {
            'city': str,
            'description': str,
            'images': list of str,
            'latitude': num,
            'longitude': num,
            'employees': list of users,
            'name': str,
            'region': str
        }

    excepts:
        401 - JWT token not valid
        404 - site id doesn't exist
    """
    site_id = request.args.get('id', type=int, )

    logger.debug("User requested site detailed info", )

    async with async_session() as session:
        site = await get_site_by_id(session, site_id)

    return (site, 200) if site is not None else ({"error": "Site not found", }, 404)


@application.route('/api/stamp_token', methods=['GET', ], )
async def stamp_token() -> Tuple[Dict[str, str], int]:
    async with async_session() as session:
        result: Optional[Dict[str, Any]] = await Employees.by_id(session, g.authenticated_user)

        if result is None:
            return {
                'error': 'Only allowed for employees!',
            }, 400

        return {
            'token': generate_stamp_token(
                g.authenticated_user,
                result['place_id'],
            ),
        }, 200


@application.route('/api/receive_stamp/<string:token>', methods=['POST', ], )
async def receive_stamp(token: str) -> Tuple[Dict[str, str], int]:
    async with async_session() as session:
        stamp: Stamp = finish_stamping(token, g.authenticated_user)

        if stamp.visitor_id == stamp.employee_id:
            return {'error': "You can't give yourself stamps!"}, 400

        if await Stamps.add_stamp(
                session,
                stamp.visitor_id,
                stamp.employee_id,
                stamp.place_id,
        ):
            return {'message': 'Stamp received!'}, 200

        return {'error': 'You already have this stamp!'}, 400


# Login and registration endpoints


@application.route('/api/registration', methods=['POST', ], )
async def registration():
    """
    Registration of the user in the Database (not OAuth) and login on success

    Needs as form argument:
    'first_name'
    'last_name'
    'email' -> valid email syntax
    'password -> 6 or more characters

    returns:
        'token' : 'long JWT token'

    excepts:
        422 - insufficient information
        422 - wrong body format
        400 - password check not passed
        400 - email check not passed
        400 - user with that email already exists
    """
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
    """
    Generate token based on email/password

    Expected arguments (in form-data):
    'email', 'password'

    returns:
    {
        'token' : 'long JWT token'
    }

    excepts:
        422 - wrong input format
        422 - insufficient information
    """
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
    """
    Generate new token based on old VALID token

    returns:
    {
        'token' : str
    }

    excepts:
        401 : token not valid
    """
    return {'token': generate_token(g.authenticated_user, ), }, 200


# User info endpoint

@application.route('/api/get_self_info', methods=['GET', ], )
async def self_info():
    """
    Get information about yourself, based on valid token

    returns:
        {long json info}

    excepts:
        401 - not authorized
    """
    user_id = g.authenticated_user

    async with async_session() as session:
        user = await get_user_info(session, user_id, )

    return user


@application.route('/api/get_user_info', methods=['GET', ], )
async def user_info():
    """
    Get info about an employee, based on ID

    params:
        id argument -> user_id

    returns:
        {long info about user}

    excepts:
        401 - not authorized
        422 - id argument missing
        404 - Employee doesn't exist // user isn't employee
    """
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

    params:
        name -> name of the picture, including the extension (.png, .jpg)

    returns:
        picture, as a file

    excepts:
        401 - invalid token
        404 - picture not found
        400 - file name not valid
        422 - name argument missing
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
    """
    Get a profile picture based on name.
    It currently doesn't check if user has access to that profile picture.

    params:
        name -> name of the picture, including the extension (.png, .jpg)

    returns:
        picture, as a file

    excepts:
        401 - invalid token
        404 - picture not found
        400 - file name not valid
        422 - name argument missing
    """
    name = request.args.get('name', type=str, )

    if name is not None:
        # regex testing if user is trying to access other parts of the OS (with..)
        if match(r'^[\w\s_+\-()]([\w\s_+\-().])+$', name) is None:
            return {"error": "Invalid site picture!", }, 400

        # TODO check if user has access to that photo

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
def on_starting(_server):
    pass
