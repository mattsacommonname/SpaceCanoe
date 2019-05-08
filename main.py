from calendar import timegm
from click import argument
from datetime import datetime
from feedparser import parse
from flask import flash, Flask, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, LoginManager, logout_user, UserMixin
from flask_restful import Api, fields, marshal, Resource
from flask_wtf import FlaskForm
from pony.orm import composite_key, Database, db_session, delete, desc, Optional, PrimaryKey, Required, select, Set,\
    set_sql_debug
from uuid import UUID, uuid4
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired


# application

app = Flask(__name__)
app.secret_key = b'\x02\x94o\x97\xd4V\x8a\xb0\x91\xa8\x93\x89\x94\x80\xac\x00'


# database

db = Database()


class Source(db.Entity):
    feed_uri = Required(str, unique=True)
    entries = Set('Entry')
    label = Required(str)
    last_check = Required(datetime)
    last_fetch = Required(datetime)
    link = Required(str)


class Entry(db.Entity):
    link = Required(str)
    source = Required(Source)
    summary = Optional(str)
    title = Required(str)
    updated = Required(datetime)
    composite_key(source, link, title, updated)


class UserModel(db.Entity):
    _table_ = 'User'
    user_id = PrimaryKey(UUID, default=uuid4)
    name = Required(str, unique=True)
    password_hash = Required(str)

    @classmethod
    def build(cls, name, password):
        password_hash = generate_password_hash(password)
        user = UserModel(name=name, password_hash=password_hash)
        return user


db.bind(provider='sqlite', filename='data/feeds.sqlite', create_db=True)
set_sql_debug(True)
db.generate_mapping(create_tables=True)


# REST API

api = Api(app)


source_in_entry_fields = {
    'link': fields.String,
    'label': fields.String
}


entry_fields = {
    'link': fields.String,
    'source': fields.Nested(source_in_entry_fields),
    'summary': fields.String,
    'title': fields.String,
    'updated': fields.DateTime
}


class Entries(Resource):
    decorators = [login_required]

    @staticmethod
    def get():
        with db_session:
            result = select(e for e in Entry).order_by(desc(Entry.updated))
            entries = list(result)
            output = marshal(entries, entry_fields)
            return output


api.add_resource(Entries, '/entries')


# login management

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    def __init__(self, user_id: UUID, name: str):
        self.user_id = user_id
        self.name = name

    def get_id(self):
        id_text = str(self.user_id)
        return id_text


@login_manager.user_loader
def load_user(user_id):
    with db_session:
        model = UserModel[user_id]
        if not model:
            return None

        user = User(model.user_id, model.name)
        return user


# forms

class LoginForm(FlaskForm):
    name = StringField('User name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


# cli

@app.cli.command()
@argument('name')
@argument('password')
def adduser(name, password):
    with db_session:
        model = UserModel.get(name=name)
        if model:
            print(f'User "{name}" already exists.')
            return

        UserModel.build(name, password)


@app.cli.command()
@argument('uri_file_path')
def reset(uri_file_path):
    earliest = datetime.min
    with db_session:
        delete(s for s in Source)
        delete(e for e in Entry)

        with open(uri_file_path) as f:
            for line in f:
                uri = line.strip()
                if not uri:
                    continue

                feed = parse(uri)
                Source(feed_uri=uri, label=feed['feed']['title'], last_check=earliest, last_fetch=earliest,
                       link=feed['feed']['link'])


@app.cli.command()
def update():
    sources_processed = 0
    entries_processed = 0
    entries_added = 0

    with db_session:
        sources = select(s for s in Source)
        for source in sources:
            feed = parse(source.feed_uri)
            if feed['bozo']:
                continue

            sources_processed += 1

            for entry in feed['entries']:
                # build UTC time
                timestamp = timegm(entry['updated_parsed'])
                updated = datetime.utcfromtimestamp(timestamp)

                link = entry['link']
                title = entry['title']

                entries_processed += 1

                check = Entry.get(link=link, source=source, title=title, updated=updated)
                if check is not None:
                    continue

                entries_added += 1

                Entry(link=link, source=source, summary=entry['summary'], title=title, updated=updated)

    print(f'sources processed\t{sources_processed}\nentries processed\t{entries_processed}',
          f'entries added\t{entries_added}', sep='\n')


# routes

@app.route('/login', methods=['POST'])
def login():
    url = url_for('root')
    output = redirect(url)

    form = LoginForm()
    if not form.validate_on_submit():
        flash('User login failed.', 'error')
        return output

    name = form.name.data
    password = form.password.data

    with db_session:
        model = UserModel.get(name=name)
        if not model or not check_password_hash(model.password_hash, password):
            flash('User login failed.', 'error')
            return output

        user = User(model.user_id, model.name)
        login_user(user, remember=True)
        flash(f'User "{name}" logged in.', 'info')

        return output


@app.route('/logout')
@login_required
def logout():
    name = current_user.name
    logout_user()
    flash(f'User "{name}" logged out.', 'info')
    url = url_for('root')
    output = redirect(url)
    return output


@app.route('/')
def root():
    login_form = LoginForm()
    output = render_template('root.html', login_form=login_form)
    return output
