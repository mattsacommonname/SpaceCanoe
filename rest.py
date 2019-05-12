from flask_login import login_required
from flask_restful import fields, marshal, Resource
from pony.orm import db_session, desc, select

from database import Entry as EntryModel, Source as SourceModel, Tag as TagModel


# entries

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
            result = select(e for e in EntryModel).order_by(desc(EntryModel.updated))
            entries = list(result)
            output = marshal(entries, entry_fields)
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
    'tags': fields.List(fields.Nested(tag_in_source_fields))
}


class Sources(Resource):
    decorators = [login_required]

    @staticmethod
    def get():
        with db_session:
            result = select(s for s in SourceModel).order_by(SourceModel.label)
            sources = list(result)
            output = marshal(sources, source_fields)
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
            result = select(t for t in TagModel).order_by(TagModel.label)
            tags = list(result)
            output = marshal(tags, tag_fields)
            return output
