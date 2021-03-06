# System imports
import os
import traceback
from os import path
from re import match
from typing import List, Any, Dict, Optional, Tuple

# Dependency imports
from quart import Quart, request, send_file, g
from quart_cors import cors

from src.database.rewards_log import RewardsLog

# Own imports
from .exceptions import BadUserRequest, RaisedFrom, ServerException
from .response_formatters import get_employee_info, get_site_by_id, get_tourist_sites, get_self_info, get_user_info, get_user_eligible_rewards
from .auth import AuthenticationError, validate_token, verify_password, generate_token, hash_password
from .config.logger_config import logger
from .database import db_init, async_session
from .database.local_users import LocalUsers
from .database.stamps import Stamps
from .database.employees import Employees
from .google_api import google_api
from .stamps import InvalidStamp, make_stamp, Stamp
from .id_token import generate_id_token, InvalidIdToken, get_id_from_token
from .utils.all_sites_filter import AllSitesFilter
from .utils.enviromental_variables import PORT

UNAUTHENTICATED_URLS: List[str] = [
    '/api/login',
    '/api/registration',
    '/api/oauth2/google',
    # '/imageserver/tourist_sites',
    # '/imageserver/profile_pictures'
]

application = Quart(__name__, )
application = cors(
    application,
    allow_origin="*",
    allow_headers=['Authorization', 'Content-Type', ],
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


def server_exception_handler(ex: Exception) -> Tuple[Dict[str, Any], int]:
    if not isinstance(ex, ServerException):
        return {'error': 'Internal Server Error! Wrong exception handler used!', }, 500

    server_exception: ServerException = ex

    del ex

    traceback.print_exception(
        type(server_exception), server_exception, server_exception.__traceback__, )

    if isinstance(server_exception, RaisedFrom):
        traceback.print_exception(
            type(server_exception.source_exception),
            server_exception.source_exception,
            server_exception.source_exception.__traceback__,
        )

    return {'error': server_exception.message, }, server_exception.http_code


application.register_error_handler(
    ServerException,
    server_exception_handler,
)


@application.before_request
def auth_before_request():
    """
    Validates Auth token in Authorization header. Executes before every
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
            'id' : int,
            'city':str,
            'image':str,
            'name':str,
            'region':str
            'is_stamped':bool
        },
    ]

    excepts:
        401: Auth token not valid
        400: filter not valid
    """

    site_type = request.args.get('filter', type=str, )

    try:
        site_type = AllSitesFilter(site_type)
    except ValueError:
        # TODO make expected synced with ENUM
        return {"error": "Incorrect information",
                "expected": "'filter' : 'all' / 'visited' / 'unvisited' as an argument"}, 400

    logger.debug(f"User {g.authenticated_user} requested all site info")

    async with async_session.begin() as session:
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
        401 - Auth token not valid
        404 - site id doesn't exist
    """
    site_id = request.args.get('id', type=int, )

    logger.debug(
        f"User {g.authenticated_user} requested site {site_id} detailed info")

    async with async_session.begin() as session:
        site = await get_site_by_id(session, site_id)

    return (site, 200) if site is not None else ({"error": "Site not found", }, 404)

# Identification endpoint


@application.route('/api/get_id_token', methods=['GET', ], )
async def id_token() -> Tuple[Dict[str, str], int]:
    """
    Parameter for getting an identification token to be scanned (via QR)
    Token has a 30sec validity.

    returns:
        {"id_token" : str}

    excepts:
        401: Not logged in
        401: not employee
        400: Employee without assigned place

    """
    logger.debug(
        f"user with id {g.authenticated_user} requested a ID token")

    return {
        'id_token': generate_id_token(
            g.authenticated_user,
        ),
    }, 200

# Stamipng endpoint


@application.route('/api/make_stamp', methods=['POST', ], )
async def receive_stamp() -> Tuple[Dict[str, str], int]:
    """
    Endpoint for receiving a stamp from a scanned token.

    args:
        'id_token' : str -> scanned token

    returns:
        {"message" : str} on success

    excepts:
        401: not authorized
        400: expired/invalid token
        400: employee trying to give himself a stamp
        400: already have this stamp
    """
    async with async_session.begin() as session:

        # Make a stamp object
        id_token: str = (await request.form).get('id_token')
        logger.debug(f"User (id:{g.authenticated_user}) requested a stamp")

        try:
            stamp: Stamp = await make_stamp(
                session, id_token, g.authenticated_user)
            logger.debug("Stamp successfully made!")
        except (InvalidStamp):
            return {'error': "The stamp token has expired or isn't valid or user isn't employee!"}, 400

        if stamp.visitor_id == stamp.employee_id:
            logger.warning(
                f'Employee (id:{g.authenticated_user}) tried to give themselves a stamp')
            return {'error': "You can't give yourself stamps!"}, 400

        # If adding stamp to DB is successful
        if await Stamps.add_stamp(session, stamp):
            logger.debug("Stamp saved to Database")
            return {'message': 'Stamp received!'}, 200

        logger.debug("Stamp already exists")
        return {'message': 'You already have this stamp!'}, 200


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
        'token' : 'long Auth token'

    excepts:
        422 - insufficient information
        422 - wrong body format
        400 - password check not passed
        400 - email check not passed
        400 - user with that email already exists
    """
    logger.debug("New user registration")
    form = await request.form

    if form is None:
        logger.debug("User provided wrong request format")
        return {"error": "Wrong request body!"}

    first_name: Optional[str] = form.get('first_name', type=str, )
    last_name: Optional[str] = form.get('last_name', type=str, )
    email: Optional[str] = form.get('email', type=str, )
    password: Optional[str] = form.get('password', type=str, )

    # If we don't have all the needed info, return
    if None in (first_name, last_name, email, password):
        logger.debug("User didn't fill all needed information")
        return {
            'error': 'insufficient information',
            'expected': [
                'first_name',
                'last_name',
                'email',
                'password',
            ],
        }, 422

    # Password check
    # TODO make more sophisticated
    if len(password) < 6:
        logger.debug("Password check failed")
        return {'error': 'Password too short. It must be 6 characters or longer', }, 400

    user_id: int

    async with async_session.begin() as session:
        user_id: int = await LocalUsers.insert(
            session,
            first_name,
            last_name,
            email,
            hash_password(password),
        )

    logger.debug("Registration success!")

    return {'token': generate_token(user_id, ), }, 200


@application.route('/api/login', methods=['POST', ], )
async def login():
    """
    Generate token based on email/password

    Expected arguments (in form-data):
    'email', 'password'

    returns:
    {
        'token' : 'long Auth token'
    }

    excepts:
        422 - wrong input format
        422 - insufficient information
    """
    logger.debug("User login request")
    form = await request.form

    if form is None:
        logger.debug("User provided wrong request format")
        return {"error": "Wrong request body!"}, 400

    email = form.get('email', type=str, )
    password = form.get('password', type=str, )

    if None in (email, password,):
        logger.debug("User didn't provide enough info")
        return {"error": "Insufficient information", }, 422

    async with async_session.begin() as session:
        user_id, pw_hash = await LocalUsers.by_email(session, email, )

        if verify_password(password, pw_hash, ):
            logger.debug(f"Successful login for (id: {user_id})")
            return {'token': generate_token(user_id, ), }, 200

        logger.debug("Unsuccessful login")
        # returns 400 error
        raise AuthenticationError()


@application.route('/api/oauth2/google', methods=['GET', ], )
async def google_oauth2():
    logger.warning("OAuth called!")
    logger.debug(google_api.authorization_url(), )
    logger.debug(request.args, )

    raise AuthenticationError()


@application.route('/api/refresh_token', methods=['GET', ], )
async def refresh_token():
    """
    Generate new token based on old VALID token

    returns:
        'token' : str

    excepts:
        401 : token not valid
    """
    logger.debug(f"user {g.authenticated_user} requested token refresh")
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
    logger.debug(f'User {user_id} requested self info')
    async with async_session.begin() as session:
        user = await get_self_info(session, user_id, )

    return user, 200


@application.route('/api/get_employee_info', methods=['GET', ], )
async def employee_info():
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
    logger.debug(f"user {g.authenticated_user} requested info about {user_id}")

    if user_id is None:
        return {"error": "Insufficient information", }, 422

    async with async_session.begin() as session:
        employee = await get_employee_info(session, user_id, )
        if employee is None:
            logger.warning(
                f"user with id:{g.authenticated_user} requested info about a non-employee!")
            return {"error": "Employee doesn't exist!", }, 404
        else:
            return employee, 200


@application.route('/api/get_user_info', methods=['GET'], )
async def user_info():
    """
    Get info about a user, based on ID

    params:
        id argument -> user_id

    returns:
        {info about user}

    excepts:
        401 - not authorized
        422 - id argument missing
        404 - user doesn't exist
    """
    user_id = request.args.get('id', type=int, )

    logger.debug(
        f"User with id:{g.authenticated_user} requested user info about id:{user_id}")

    if user_id is None:
        return {"error": "Insufficient information", }, 422

    async with async_session.begin() as session:
        user = await get_user_info(session, user_id, )
        return ({"error": "User doesn't exist!", }, 404) if user is None else (user, 200)


# rewards endpoints

@application.route('/api/get_eligible_rewards', methods=['GET'], )
async def eligible_rewards():
    """
    Request for employees to see what rewards they can give to a certain user

    params:
        id_token : str -> user id token from get_id_token endpoint

    returns:
        {received_rewards: list(dict),
         eligible_rewards: list(dict)}

    excepts:
        401: Employee not authorized
        401: user is not employee
        422: wrong body type / insufficient information
        400: Expired/invalid ID token
    """
    async with async_session.begin() as session:

        if not await Employees.exists(session, g.authenticated_user):
            return {"error": "You are not authorized for this command!"}, 401

        id_token = request.args.get('id_token', type=str)
        if id_token is None:
            return {"error": "Insufficient information!", "expected": "id_token as an argument"}, 422

        try:
            rewards = await get_user_eligible_rewards(session, id_token)
        except(InvalidIdToken):
            return {"error": "Expired or Invalid ID token"}, 400

        return rewards, 200


@application.route('/api/post_reward', methods=['POST'], )
async def post_reward():
    """
    Endpoint for registering a reward in the db

    excepts:
        401: user not authorized
        401: user not employee
        401: employee can't give rewards
        422: Insufficient information or wrong body type
        400: user already has this reward
        400: user isn't eligible to recieve the reward or reward doesn't exist
        400: expired or invalid ID token
    """
    async with async_session.begin() as session:

        employee = await Employees.by_id(session, g.authenticated_user)

        if employee is None:
            return {"error": "You are not authorized for this command!"}, 401

        if not employee.get("can_reward"):
            return {"error": "You can't give out rewards! Please contact an admin!"}, 401

        form = await request.form

        id_token = form.get('id_token', type=str)
        reward_id = form.get('reward_id', type=int)
        logger.debug(f"id_token : {id_token}, reward_id : {reward_id}")
        if None in (reward_id, id_token):
            return {"error": "Insufficient information!", "expected": "id_token and reward_id as form-data"}, 422

        try:
            if await RewardsLog.insert(session, get_id_from_token(id_token), reward_id, g.authenticated_user):
                return {"message": "Reward given!"}, 200
            return {"error": "User already recieved this reward!"}, 400
        except BadUserRequest:
            return {"error": "User isn't eligible or reward doesn't exist!"}, 400
        except InvalidIdToken:
            return {"error": "Expired or invalid ID token"}, 400


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

    logger.debug(f"user requested site picture : {name}")

    if name is not None:
        # Ensure user is not accessing other parts of the OS
        if match(r'^[\w\s_+\-()]([\w\s_+\-().])+$', name) is None:
            return {"error": "Invalid site picture!", }, 400

        # Make the path of the picture
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

    logger.debug(f"user requested profile picture : {name}")

    if name is not None:
        # regex testing if user is trying to access other parts of the OS (with..)
        if match(r'^[\w\s_+\-()]([\w\s_+\-().])+$', name) is None:
            return {"error": "Invalid profile picture!", }, 400

        # TODO check if user has access to that photo

        file_path = os.path.join(
            'public',
            'profile_pictures',
            name,
        )

        if path.isfile(file_path):
            return await send_file(file_path, mimetype='image/gif')
        else:
            return {"error": "Picture not found", }, 404

    return {"error": "Insufficient information!", }, 422


@application.route('/imageserver/rewards', methods=['GET'], )
async def reward_pictures():
    """
    Get a reward photo based on name.

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

    logger.debug(f"user requested profile picture : {name}")

    if name is not None:
        # regex testing if user is trying to access other parts of the OS (with..)
        if match(r'^[\w\s_+\-()]([\w\s_+\-().])+$', name) is None:
            return {"error": "Invalid profile picture!", }, 400

        file_path = os.path.join(
            'public',
            'rewards',
            name,
        )

        if path.isfile(file_path):
            return await send_file(file_path, mimetype='image/gif')
        else:
            return {"error": "Picture not found", }, 404

    return {"error": "Insufficient information!", }, 422

# ###### WEB SERVER START ######


def manual_run():
    application.run(host='0.0.0.0', port=PORT, debug=True, )


# Put anything that you want to start from Gunicorn master process here
def on_starting(_server):
    pass
