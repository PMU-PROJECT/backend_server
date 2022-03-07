import configparser
import os

conf = configparser.ConfigParser()
conf.read(os.path.join("conf.cfg"))

# Web
PORT = int(conf['WEB']['port'])

# Database
USER = conf['Database']['user']
PASS = conf['Database']['pass']
HOST = conf['Database']['host']
DATABASE = conf['Database']['database']
