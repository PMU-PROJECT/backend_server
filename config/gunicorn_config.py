from utils.enviromental_variables import PORT
import app

bind = f'0.0.0.0:{PORT}'

# Server Hooks
on_starting = app.on_starting
