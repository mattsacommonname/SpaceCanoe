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


from collections import OrderedDict
from flask_login import current_user, login_required
from flask_restful import fields, marshal, Resource
from pony.orm import db_session, desc, select
from pony.orm.core import Query
from typing import Callable, List

from database import Entry as EntryModel, SourceUserData as SourceUserDataModel, Tag as TagModel, User as UserModel


def get_user_data_for_entry(entry: EntryModel) -> SourceUserDataModel:
    """Gets the source user data for the given entry's source and the logged-in user.

    :param entry: The entry who's source we're looking up.
    :return: The related source user data.
    """

    user: UserModel = UserModel[current_user.user_id]
    user_data: SourceUserDataModel = SourceUserDataModel.get(source=entry.source, user=user)

    return user_data


# entries

source_in_entry_fields: dict = {
    'id': fields.Integer(attribute='source.id'),
    'link': fields.String(attribute='source.link'),
    'label': fields.String,
    'tags': fields.List(fields.String(attribute='label'))
}


entry_fields: dict = {
    'id': fields.Integer,
    'link': fields.String,
    'source': fields.Nested(source_in_entry_fields, attribute=get_user_data_for_entry),
    'summary': fields.String,
    'title': fields.String,
    'updated': fields.DateTime
}


class Entries(Resource):
    """REST endpoint for feed entries."""

    decorators: List[Callable] = [login_required]

    @staticmethod
    def get() -> List[OrderedDict]:
        """Returns all feed entries for sources the logged-in user is subscribed to.

        :return: The entries, as a list of JSON-serializable dicts.
        """

        with db_session:
            # get a list of entries from sources of feeds followed by the logged-in user
            user: UserModel = UserModel[current_user.user_id]
            sources: Query = select(s.source for s in user.sources)
            result: Query = select(e for e in EntryModel if e.source in sources).order_by(desc(EntryModel.updated))
            entries: List[EntryModel] = list(result)

            # marshall them to JSON-serializable dicts
            output: List[OrderedDict] = marshal(entries, entry_fields)
            return output


# sources

tag_in_source_fields: dict = {
    'id': fields.Integer,
    'label': fields.String
}


source_fields: dict = {
    'feed_uri': fields.String(attribute='source.feed_uri'),
    'id': fields.Integer(attribute='source.id'),
    'label': fields.String,
    'last_check': fields.DateTime(attribute='source.last_check'),
    'last_fetch': fields.DateTime(attribute='source.last_fetch'),
    'link': fields.String(attribute='source.link'),
    # TODO: pick one tag field
    'tag_labels': fields.List(fields.String(attribute='label'), attribute='tags'),
    # 'tag_objects': fields.List(fields.Nested(tag_in_source_fields), attribute='tags')  # TODO: fix, still broken
}


class Sources(Resource):
    """REST endpoint for feed sources."""

    decorators = [login_required]

    @staticmethod
    def get() -> List[OrderedDict]:
        """Returns all sources the logged-in user is subscribed to.

        :return: The sources, as a list of JSON-serializable dicts.
        """

        with db_session:
            # get a list of sources followed by the logged-in user
            user: UserModel = UserModel[current_user.user_id]
            sources: List[SourceUserDataModel] = list(user.sources)

            # marshall them to JSON-serializable dicts
            output: List[OrderedDict] = marshal(sources, source_fields)
            return output


# tags

tag_fields: dict = {
    'id': fields.Integer,
    'label': fields.String
}


class Tags(Resource):
    """REST endpoint for feed tags."""

    decorators = [login_required]

    @staticmethod
    def get() -> List[OrderedDict]:
        """Returns all tags defined by the logged-in user.

        :return: The tags, as a list of JSON-serializable dicts.
        """

        with db_session:
            # get tags from the user
            user: UserModel = UserModel[current_user.user_id]
            tags: List[TagModel] = list(user.tags)

            # marshall them to JSON-serializable dicts
            output: List[OrderedDict] = marshal(tags, tag_fields)
            return output
