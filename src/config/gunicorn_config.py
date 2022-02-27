from .. import app
from ..utils.enviromental_variables import PORT


bind = f'0.0.0.0:{PORT}'

# Server Hooks
on_starting = app.on_starting
