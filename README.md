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

- In `installdir/data/pg_hba.conf`, insert `host all all samenet scram-sha-256`

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
        "token" = "long JWT token"
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
        "token" = "long JWT token"
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

- `/api/get_site_info` [GET]

  the requests expect the parameter as an argument:
    - `filter` -> all, visited, unvisited

  if filter is valid, returns:
    ```

{
"city": str,
"description": str,
"employees": [ # Only if employees are assigned {
"added_by": int,
"can_reward": bool,
"email": str,
"first_name": str,
"last_name": str,
"place_id": int,
"profile_picture": str }
],
"images": [
str,
],
"latitude": str,
"longitude": str,
"name": str,
"region": str }

```

- `/api/refresh-token` [POST]

  the request requires header:
  `Authorization` : valid JWT token

  if token is valid, returns:
    ```
    {
        'token' : 'long JWT token'
    }
    ```

- `/api/get_self_info` [GET]

  the request requires header:
  `Authorization` : valid JWT token

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

- `/api/get_user_info` [GET]

  You currently get info about employees only

  the request requires header:
  `Authorization` : valid JWT token

  the request requires the param as argument:
  `id` : user_id

  upon valid JWT token and id, returns:
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
- `/imageserver/tourist_sites` [GET]

  the request requires header:
  `Authorization` : valid JWT token

  the request requires the param as argument:
  `name` : picture name **with** extension (.jpg, .png)

  if name and JWT token valid, returns photo

- `/imageserver/profile_pictures` [GET]

  the request requires header:
  `Authorization` : valid JWT token

  the request requires the param as argument:
  `name` : picture name **with** extension (.jpg, .png)

  if name and JWT token valid, returns photo