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


from datetime import datetime
from pony.orm import composite_key, Database, Optional, PrimaryKey, Required, Set
from uuid import UUID, uuid4
from werkzeug.security import generate_password_hash

db = Database()


class Entry(db.Entity):
    link = Required(str)
    source = Required('Source')
    summary = Optional(str)
    title = Required(str)
    updated = Required(datetime)
    composite_key(source, link, title, updated)


class Source(db.Entity):
    feed_uri = Required(str, unique=True)
    entries = Set(Entry)
    label = Required(str)
    last_check = Required(datetime)
    last_fetch = Required(datetime)
    link = Required(str)
    tags = Set('Tag')
    users = Set('User')


class Tag(db.Entity):
    label = Required(str, unique=True)
    sources = Set(Source)


class User(db.Entity):
    user_id = PrimaryKey(UUID, default=uuid4)
    name = Required(str, unique=True)
    password_hash = Required(str)
    sources = Set(Source)

    @classmethod
    def build(cls, name, password):
        password_hash = generate_password_hash(password)
        user = User(name=name, password_hash=password_hash)
        return user
