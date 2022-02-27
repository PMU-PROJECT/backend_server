# System imports
import json

# Dependency imports
from quart import Quart, request

# Own imports
from .config.logger_config import logger
from .utils.enviromental_variables import PORT
from .database import db_init


application = Quart(__name__)

application.before_serving(db_init)


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
def manual_run():
    application.run(host='0.0.0.0', port=PORT)


# Put anything that you want to start from Gunicorn master proccess here
def on_starting(server):
    pass
