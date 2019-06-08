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


from flask_login import current_user, login_required
from flask_restful import fields, marshal, Resource
from pony.orm import db_session, desc, select

from database import Entry as EntryModel, Source as SourceModel, Tag as TagModel, User as UserModel


def iterable_tags_attribute(source: SourceModel):
    """Figure out the appropriate tags for this source in relation to the current_user.

    This must be called in a context where

    :param source: The source to pull the tags from.
    :return: A list of tag models.
    """

    user = UserModel[current_user.user_id]
    tags = [t for t in source.tags if t.user == user]

    return tags


# entries

source_in_entry_fields = {
    'id': fields.Integer,
    'link': fields.String,
    'label': fields.String,
    'tags': fields.List(fields.String(attribute='label'), attribute=iterable_tags_attribute)
}


entry_fields = {
    'id': fields.Integer,
    'link': fields.String,
    'source': fields.Nested(source_in_entry_fields),
    'summary': fields.String,
    'title': fields.String,
    'updated': fields.DateTime
}


class Entries(Resource):
    """REST endpoint for feed entries."""

    decorators = [login_required]

    @staticmethod
    def get():
        """Returns all feed entries for sources the logged-in user is subscribed to."""

        with db_session:
            user = UserModel[current_user.user_id]
            result = select(e for e in EntryModel if user in e.source.users).order_by(desc(EntryModel.updated))
            entries = list(result)
            output = marshal(entries, entry_fields)
            return output


# sources

tag_in_source_fields = {
    'id': fields.Integer,
    'label': fields.String
}


source_fields = {
    'feed_uri': fields.String,
    'id': fields.Integer,
    'label': fields.String,
    'last_check': fields.DateTime,
    'last_fetch': fields.DateTime,
    'link': fields.String,
    # TODO: pick one tag field
    'tag_labels': fields.List(fields.String(attribute='label'), attribute=iterable_tags_attribute),
    'tag_objects': fields.List(fields.Nested(tag_in_source_fields), attribute=iterable_tags_attribute)
}


class Sources(Resource):
    """REST endpoint for feed sources."""

    decorators = [login_required]

    @staticmethod
    def get():
        """Returns all sources the logged-in user is subscribed to."""

        with db_session:
            user = UserModel[current_user.user_id]
            result = select(s for s in SourceModel if user in s.users)
            entries = list(result)
            output = marshal(entries, source_fields)
            return output


# tags

tag_fields = {
    'id': fields.Integer,
    'label': fields.String
}


class Tags(Resource):
    """REST endpoint for feed tags."""

    decorators = [login_required]

    @staticmethod
    def get():
        """Returns all tags defined by the logged-in user."""

        with db_session:
            user = UserModel[current_user.user_id]
            result = select(t for t in TagModel if t.user == user).order_by(TagModel.label)
            entries = list(result)
            output = marshal(entries, tag_fields)
            return output
