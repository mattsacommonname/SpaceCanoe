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


from flask_login import login_required
from flask_restful import fields, marshal, Resource
from pony.orm import db_session, desc, select

from database import Entry as EntryModel, Source as SourceModel, Tag as TagModel


def iterable_tags_attribute(source: SourceModel):
    tags = source.tags.copy()
    return tags


def get_rest_output(model, order, field_definitions):
    result = select(x for x in model).order_by(order)
    entries = list(result)
    output = marshal(entries, field_definitions)
    return output


# entries

source_in_entry_fields = {
    'link': fields.String,
    'label': fields.String,
    'tags': fields.List(fields.String(attribute='label'), attribute=iterable_tags_attribute)
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
            output = get_rest_output(EntryModel, desc(EntryModel.updated), entry_fields)
            return output


# sources

tag_in_source_fields = {
    'label': fields.String
}


source_fields = {
    'feed_uri': fields.String,
    'label': fields.String,
    'last_check': fields.DateTime,
    'last_fetch': fields.DateTime,
    'link': fields.String,
    # TODO: pick one tag field
    'tag_labels': fields.List(fields.String(attribute='label'), attribute=iterable_tags_attribute),
    'tag_objects': fields.List(fields.Nested(tag_in_source_fields), attribute=iterable_tags_attribute)
}


class Sources(Resource):
    decorators = [login_required]

    @staticmethod
    def get():
        with db_session:
            output = get_rest_output(SourceModel, SourceModel.label, source_fields)
            return output


# tags

tag_fields = {
    'label': fields.String
}


class Tags(Resource):
    decorators = [login_required]

    @staticmethod
    def get():
        with db_session:
            output = get_rest_output(TagModel, TagModel.label, tag_fields)
            return output
