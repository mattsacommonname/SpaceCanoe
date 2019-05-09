from datetime import datetime
from pony.orm import composite_key, Database, Optional, PrimaryKey, Required, Set
from uuid import UUID, uuid4
from werkzeug.security import generate_password_hash

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


class User(db.Entity):
    user_id = PrimaryKey(UUID, default=uuid4)
    name = Required(str, unique=True)
    password_hash = Required(str)

    @classmethod
    def build(cls, name, password):
        password_hash = generate_password_hash(password)
        user = User(name=name, password_hash=password_hash)
        return user
