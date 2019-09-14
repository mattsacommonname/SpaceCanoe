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
from pony.orm import (
    composite_key,
    Database,
    Optional,
    PrimaryKey,
    Required,
    Set)
from pony.orm.core import Attribute
from uuid import (
    UUID,
    uuid4)
from werkzeug.security import generate_password_hash

db = Database()


class Entry(db.Entity):
    """An individual entry in a feed."""

    link: Attribute = Required(str)
    source: Attribute = Required('Source')
    summary: Attribute = Optional(str)
    title: Attribute = Required(str)
    updated: Attribute = Required(datetime)
    composite_key(source, link, title, updated)


class Source(db.Entity):
    """Feed source. Contains information for retrieving a feed, and some display information."""

    feed_uri: Attribute = Required(str, unique=True)
    entries: Attribute = Set(Entry)
    fetched_label: Attribute = Required(str)
    last_check: Attribute = Required(datetime)
    last_fetch: Attribute = Required(datetime)
    link: Attribute = Required(str)
    user_data: Attribute = Set('SourceUserData')


class SourceUserData(db.Entity):
    """User-specific data for feed sources."""

    source: Attribute = Required(Source)
    tags: Attribute = Set('Tag')
    user: Attribute = Required('User')
    user_label: Attribute = Optional(str)
    composite_key(source, user)

    @property
    def label(self) -> str:
        """Returns the display label for the source.

        If there's a user-defined label, uses that, otherwise uses the label fetched from the feed.

        :return: A string of the display label.
        """

        return self.user_label or self.source.fetched_label


class Tag(db.Entity):
    """Organizational tag for feed sources."""

    label: Attribute = Required(str)
    sources: Attribute = Set(SourceUserData)
    user: Attribute = Required('User')
    composite_key(label, user)


class User(db.Entity):
    """User."""

    user_id: Attribute = PrimaryKey(UUID, default=uuid4)
    name: Attribute = Required(str, unique=True)
    password_hash: Attribute = Required(str)
    sources: Attribute = Set(SourceUserData)
    tags: Attribute = Set(Tag)

    @classmethod
    def build(cls, name: str, password: str) -> 'User':
        """Generate a user with a properly hashed password.

        :param name: Username to use.
        :param password: Plaintext password.
        :return: A new user object.
        """

        password_hash = generate_password_hash(password)
        user: User = User(name=name, password_hash=password_hash)

        return user
