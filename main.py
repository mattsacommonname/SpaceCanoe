# Copyright 2019 Matthew Bishop
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from flask import Flask
from flask_restful import Api
from pony.orm import set_sql_debug

from cli import AddUserCommand, UpdateCommand
from database import db
from login import login_manager
from rest import Entries as EntryResource, Sources as SourceResource, Tags as TagResource
from routes import add_feed as add_feed_route, login as login_route, logout as logout_route, root as root_route,\
    upload_opml as upload_opml_route


# application

app: Flask = Flask(__name__)
app.config.from_pyfile('data/config.py')


# database

db.bind(**app.config['PONY_BINDINGS'])
set_sql_debug(app.config['DEBUG'])
db.generate_mapping(**app.config['PONY_MAPPINGS'])


# REST API

api: Api = Api(app)
api.add_resource(EntryResource, '/entries')
api.add_resource(SourceResource, '/sources')
api.add_resource(TagResource, '/tags')


# login management

login_manager.init_app(app)


# cli

app.cli.add_command(AddUserCommand)
app.cli.add_command(UpdateCommand)


# routes

app.add_url_rule('/', view_func=root_route)
app.add_url_rule('/add_form', view_func=add_feed_route, methods=['POST'])
app.add_url_rule('/login', view_func=login_route, methods=['POST'])
app.add_url_rule('/logout', view_func=logout_route)
app.add_url_rule('/upload_opml', view_func=upload_opml_route, methods=['POST'])


if __name__ == '__main__':
    app.run(debug=True, passthrough_errors=True, use_debugger=False, use_reloader=False)
