from flask import Flask
from flask_restful import Api
from pony.orm import set_sql_debug

from cli import AddUserCommand, ResetCommand, UpdateCommand
from database import db
from login import login_manager
from rest import Entries as EntryResource
from routes import login as login_route, logout as logout_route, root as root_route


# application

app = Flask(__name__)
app.secret_key = b'\x02\x94o\x97\xd4V\x8a\xb0\x91\xa8\x93\x89\x94\x80\xac\x00'


# database

db.bind(provider='sqlite', filename='data/feeds.sqlite', create_db=True)
set_sql_debug(True)
db.generate_mapping(create_tables=True)


# REST API

api = Api(app)
api.add_resource(EntryResource, '/entries')


# login management

login_manager.init_app(app)


# cli

app.cli.add_command(AddUserCommand)
app.cli.add_command(ResetCommand)
app.cli.add_command(UpdateCommand)


# routes

app.add_url_rule('/', view_func=root_route)
app.add_url_rule('/login', view_func=login_route, methods=['POST'])
app.add_url_rule('/logout', view_func=logout_route)
