from views import start_up
from views import app
from constants import users_view, passwords_view

start_up(flask_api_status=True, users=users_view, passwords=passwords_view)
app = app
# app.run(use_reloader = False)


