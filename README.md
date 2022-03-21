# PMU backend server

---

## Web server

The server runs on Quart 0.16.3. We are using Hypercorn as an ASGI server for production. The app runs on port 37888 (by
default).

---

## Running the app

1. **Google**

- Create a Google API account
- Create a client secret
- put client_secret.json in root project folder

2. **Database**

allow connection from all IPs (to allow docker hypercorn container to run)

**For Windows PostgreSQL 14**
- In installdir/data/pg_hba.conf, insert
- `host all             all              samenet              scram-sha-256`

**For Debian PostgreSQL 13 on ARM64**
- log in as a postgre user, to see the postgre config files. Type `sudo su postgres` in the terminal
- coordinate to `/etc/postgresql/13/main`
- type `nano pg_hba.conf` and add the following line
- `host all             all              samenet              md5`
- type `nano postgresql.conf` and find the `listen_adresses` line
- change the value from `"localhost"` to `"*"` 

Make a Database and a User, able to alter the database

3. **conf.cfg creation**

- Copy the `conf.cfg.example` file, while renaming it to just `conf.cfg`
- If you want to change the port (from 37888), change it in the docker-compose.yml as well
- If your database is NOT running on your host machine, change the host parameter.

4. **Development run with Quart**

- Open a terminal in the root folder and type `py quart_manual_run.py` to start a single worker

5. **Production run with Hypercorn**

- Install docker
- open directory of project
- type `docker-compose up` in the terminal to start the container
- type `docker-compose down` in the terminal to stop the container

---

## API documentation

1. Login and registration

You can register/login in the app using our internal protocol, or OAuth2 and google (currently not implemented).

- `/api/register` [POST]

  The request expects the parameters as a form:
    - `first_name`
    - `last_name`
    - `email` -> valid email syntax
    - `password` -> 6 characters or more

  Upon successful registration, the server returns a JSON token with 3 hours validity:
    ```
    {
        "token" = "long Auth token"
    }
    ```

  Excepts:
    - 422 - insufficient information
    - 422 - wrong body format
    - 400 - password check not passed
    - 400 - email check not passed
    - 400 - user with that email already exists

- `/api/login` [POST]

  The request expects the parameters as a form:
    - `email` -> valid email syntax
    - `password` -> 6 characters or more

  Upon successful login, the server returns a JSON token with 3 hours validity:
    ```
    {
        "token" = "long Auth token"
    }
    ```

  Excepts:
    - 422 - wrong input format
    - 422 - insufficient information

- `/api/oauth2/google` [POST]
  Currently not functional

- `/api/get_all_sites` [GET]

  the requests expect the parameter as an argument:
    - `filter` -> all, visited, unvisited

  if filter is valid, returns:
    ```
    {
    "sites": [
        {
            "city": str,
            "image": str,
            "name": str,
            "region": str
        },
    ]
    }
    ```

    Excepts:
      401: Auth token not valid
      400: filter not valid

- `/api/get_site_info` [GET]

  the requests expect the parameter as an argument:
    - `id` -> id of the place

  if id is valid, returns:
  ```
  {
    "city": str,
    "description": str,
    "employees": 
      [ # Only if employees are assigned 
        {
        "added_by": int,
        "can_reward": bool,
        "email": str,
        "first_name": str,
        "last_name": str,
        "place_id": int,
        "profile_picture": str 
        },
      ],
    "images": [
      str,
    ],
    "latitude": str,
    "longitude": str,
    "name": str,
    "region": str 
  }
  ```

  Excepts:
    401 - Auth token not valid
    404 - site id doesn't exist

- `/api/refresh_token` [POST]

  the request requires header:
  `Authorization` : valid Auth token

  if token is valid, returns:
  ```
  {
      'token' : 'long Auth token'
  }
  ```

  Excepts:
    401 : token not valid

- `/api/get_self_info` [GET]

  the request requires header:
  `Authorization` : valid Auth token

  if token is valid, returns:
    ```
    {
    "email": str,
    "employee_info": {
        "added_by": {
            "email": str,
            "first_name": str,
            "last_name": str,
            "profile_picture": str
        },
        "can_reward": bool,
        "email": str,
        "first_name": str,
        "last_name": str,
        "place_id": int,
        "profile_picture": str
    },
    "first_name": str,
    "is_admin": bool,
    "last_name": str,
    "profile_picture": str,
    "stamps": [
      {
        "employee_id": int,
        "given_on": str,
        "place_id": int,
        "visitor_id": int
      }
    ]
  }
  ```

  Excepts:
    401 : not authorized


- `/api/get_user_info` [GET]

  You currently get info about employees only

  the request requires header:
  `Authorization` : valid Auth token

  the request requires the param as argument:
  `id` : user_id

  upon valid Auth token and id, returns:
  ```
  {
  "added_by": {
    "email": str,
    "first_name": str,
    "last_name": str,
    "profile_picture": str
  },
  "can_reward": bool,
  "email": str,
  "first_name": str,
  "last_name": str,
  "is_admin: bool,
  "place_id": int,
  "profile_picture": str
  }
  ```

  Excepts:
    401 - not authorized
    422 - id argument missing
    404 - Employee doesn't exist // user isn't employee

- `/api/get_stamp_token` [GET]

  For EMPLOYEES to get a stamp token, that WILL be scanned from the users

  the request requires header:
  `Authorization` : valid Auth token

  the request requires the user to be an employee

  if Auth is valid and user is employee:
  ```
  {
    "stamp_token" : str
  }
  ```

  excepts:
    401: Not logged in
    401: Not employee
    400: Employee without assigned place

- `/api/recieve_stamp` [POST]
  
  For USERS to recieve a stamp, that IS scanned from an employee

  the request requires header:
  `Authorization` : valid auth token

  the request requires the args as form-data:
  `stamp_token` : str

  if the user is authorized and token is valid:
  ```
  {
    "message" : str
  }
  ```

  Excepts:
    401: not authorized
    400: expired/invalid token
    400: employee trying to give himself a stamp
    400: already have this stamp


- `/imageserver/tourist_sites` [GET]

  the request requires header:
  `Authorization` : valid Auth token

  the request requires the param as argument:
  `name` : picture name **with** extension (.jpg, .png)

  if name and Auth token valid, returns photo

  Excepts:
    401 - invalid token
    404 - picture not found
    400 - file name not valid
    422 - name argument missing

- `/imageserver/profile_pictures` [GET]

  the request requires header:
  `Authorization` : valid Auth token

  the request requires the param as argument:
  `name` : picture name **with** extension (.jpg, .png)

  if name and Auth token valid, returns photo

  Excepts:
    401 - invalid token
    404 - picture not found
    400 - file name not valid
    422 - name argument missing