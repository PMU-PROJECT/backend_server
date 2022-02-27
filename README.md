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

allow connection from samenet IPs
- In installdir/data/pg_hba.conf, insert
- host *database_name* *database_user* 172.17.0.0/16 trust
- where you replace database_name and database_user with the ones you created

**Quart**

2.  debug 
- Open a terminal and type
- /Win/ set QUART_APP=wsgi:application /Unix/ QUART_APP=wsgi:application
- Start the application with py -m wsgi.py


**Hypercorn**