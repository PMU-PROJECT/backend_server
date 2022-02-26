# System imports
import json

# Dependency imports
from flask import Flask, request

# Own imports
from .config.logger_config import logger
from .utils.enviromental_variables import PORT
from .database import db_init


application = Flask(__name__)

application.before_first_request(application.ensure_sync(db_init))

###### REQUEST HANDLERS ######


@application.route('/get_site_info', methods=['POST'])
def interactive():
    data = json.loads(request.form.get('payload'))
    logger.debug("User requested site info")
    return '', 200


@application.route('/reset', methods=['POST'])
def reset():
    data = request.form
    return '', 200


###### WEB SERVER START ######


# For easier debugging, run with `python3 -m app` (instead of docker)
if __name__ == "__main__":
    application.run(host='0.0.0.0', port=PORT)


# Put anything that you want to start from Gunicorn master proccess here
def on_starting(server):
    pass
