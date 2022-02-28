# PMU backend server

---

## Web server

The server runs on flask 2.0.3 (async support).
We are using Gunicorn as a WSGI server for production.
The app runs on port 37888

---

## Running the app

**database**

1. If running from local machine

allow connection from all IPs
- In installdir/data/pg_hba.conf, insert
- host all             all              all              scram-sha-256

**Quart**

2.  debug 
- Open a terminal and type
- /Win/ set QUART_APP=wsgi:application /Unix/ QUART_APP=wsgi:application
- Start the application with py -m wsgi.py


**Hypercorn**

- Install docker
- open directory of project
- type `docker-compose up --build`
- After building the images, you can start it from the docker app or by typing `docker-compose up` in the terminal