import configparser
import os

conf = configparser.ConfigParser()
conf.read(os.path.join("conf.cfg"))

# Web
PORT = int(conf['WEB']['port'])

# Database
USER = conf['Database']['user']
PASS = conf['Database']['pass']
DATABASE = conf['Database']['database']

# if IN_PROD env. var. exists, set host to HOST_PROD, otherwise set to HOST_DEV
# host differs, because docker localhost =/= host localhost
HOST = conf['Database'][f'host_{"dev" if os.getenv("IN_PROD") is None else "prod"}']
