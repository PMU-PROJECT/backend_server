# PMU backend server

---

## Web server

The server runs on Quart 0.16.3.
We are using Hypercorn as a ASGI server for production.
The app runs on port 37888 (by default).

---

## Running the app

1. **Google**

- Create a google API account
- Create a client secret
- put client_secret.json in root project folder

2. **Database**

allow connection from all IPs (to allow docker hypercorn container to run)
- In installdir/data/pg_hba.conf, insert
- host all             all              samenet              scram-sha-256

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

    The request expects the parameters:
