import configparser
import os
import ast

conf = configparser.ConfigParser()
conf.read(os.path.join("config", "conf.cfg"))

# Web
PORT = int(conf['WEB']['port'])
