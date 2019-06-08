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
    """An individual entry in a feed."""

    link = Required(str)
    source = Required('Source')
    summary = Optional(str)
    title = Required(str)
    updated = Required(datetime)
    composite_key(source, link, title, updated)


class Source(db.Entity):
    """Feed source. Contains information for retrieving a feed, and some display information."""

    feed_uri = Required(str, unique=True)
    entries = Set(Entry)
    fetched_label = Required(str)
    last_check = Required(datetime)
    last_fetch = Required(datetime)
    link = Required(str)
    tags = Set('Tag')
    user_label = Optional(str)
    users = Set('User')

    @property
    def label(self):
        """Returns the display label for the source.

        If there's a user-defined label, uses that, otherwise uses the label fetched from the feed.

        :return: A string of the display label.
        """

        return self.user_label or self.fetched_label


class Tag(db.Entity):
    """Organizational tag for feed sources."""

    label = Required(str)
    sources = Set(Source)
    user = Required('User')
    composite_key(label, user)


class User(db.Entity):
    """User."""

    user_id = PrimaryKey(UUID, default=uuid4)
    name = Required(str, unique=True)
    password_hash = Required(str)
    sources = Set(Source)
    tags = Set(Tag)

    @classmethod
    def build(cls, name, password):
        """Generate a user with a password.

        :param name: Username to use.
        :param password: Plaintext password.
        :return: A new user object.
        """

        password_hash = generate_password_hash(password)
        user = User(name=name, password_hash=password_hash)

        return user
